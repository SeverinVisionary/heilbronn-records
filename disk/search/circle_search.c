/* Heilbronn triangle in the unit-radius disk: multistart SA + pattern-search polish.
 * SEARCH ONLY.  The reported value must be recomputed exactly in Python from
 * integer-scaled coordinates (circle_attack.snap_to_disk / exact_minimum).
 *
 * usage: heil n iters restarts threads seed_base
 * stdout line 1: "value x0 y0 x1 y1 ..."   (best restart)
 * stdout line 2: "#hist restarts within_abs1e-9 within_rel1e-6"
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>

#define MAXN 24
#define MAXM 2024      /* C(24,3) = 2024 */
#define MAXPP 253      /* C(23,2) = 253  */

static int N, M;
static int TA[MAXM], TB[MAXM], TC[MAXM];
static int PP[MAXN][MAXPP], PPC;

static void build_index(int n) {
    N = n; M = 0;
    for (int a = 0; a < n; a++)
        for (int b = a + 1; b < n; b++)
            for (int c = b + 1; c < n; c++) { TA[M] = a; TB[M] = b; TC[M] = c; M++; }
    PPC = (n - 1) * (n - 2) / 2;
    int cnt[MAXN]; memset(cnt, 0, sizeof(cnt));
    for (int t = 0; t < M; t++) {
        PP[TA[t]][cnt[TA[t]]++] = t;
        PP[TB[t]][cnt[TB[t]]++] = t;
        PP[TC[t]][cnt[TC[t]]++] = t;
    }
}

/* ---------------- xoshiro256** ---------------- */
typedef struct { unsigned long long s[4]; int has_g; double g; } RNG;
static inline unsigned long long rotl(unsigned long long x, int k){return (x<<k)|(x>>(64-k));}
static inline unsigned long long rnext(RNG *r){
    unsigned long long *s = r->s, res = rotl(s[1]*5ULL,7)*9ULL, t = s[1]<<17;
    s[2]^=s[0]; s[3]^=s[1]; s[1]^=s[2]; s[0]^=s[3]; s[2]^=t; s[3]=rotl(s[3],45);
    return res;
}
static void rseed(RNG *r, unsigned long long seed){
    r->has_g = 0; r->g = 0.0;
    for (int i = 0; i < 4; i++){
        seed += 0x9E3779B97F4A7C15ULL;
        unsigned long long z = seed;
        z = (z ^ (z>>30)) * 0xBF58476D1CE4E5B9ULL;
        z = (z ^ (z>>27)) * 0x94D049BB133111EBULL;
        r->s[i] = z ^ (z>>31);
    }
    for (int i = 0; i < 16; i++) rnext(r);
}
static inline double runif(RNG *r){ return (double)(rnext(r) >> 11) * (1.0/9007199254740992.0); }
static inline double rnorm(RNG *r){
    if (r->has_g){ r->has_g = 0; return r->g; }
    double u1, u2, s;
    do { u1 = 2*runif(r)-1; u2 = 2*runif(r)-1; s = u1*u1+u2*u2; } while (s >= 1.0 || s == 0.0);
    double f = sqrt(-2.0*log(s)/s);
    r->g = u2*f; r->has_g = 1; return u1*f;
}

/* ---------------- geometry ---------------- */
static inline double tri(const double *X, const double *Y, int t){
    double ax=X[TA[t]], ay=Y[TA[t]], bx=X[TB[t]], by=Y[TB[t]], cx=X[TC[t]], cy=Y[TC[t]];
    return 0.5*fabs((bx-ax)*(cy-ay) - (cx-ax)*(by-ay));
}
static void all_areas(const double *X, const double *Y, double *A){
    for (int t = 0; t < M; t++) A[t] = tri(X,Y,t);
}
static inline double amin(const double *A){
    double m = A[0];
    for (int t = 1; t < M; t++) if (A[t] < m) m = A[t];
    return m;
}
static inline void project(double *x, double *y){
    double r = sqrt((*x)*(*x) + (*y)*(*y));
    if (r > 1.0){ *x /= r; *y /= r; }
}

/* deterministic pattern search on the true min-area objective */
static double polish(double *X, double *Y){
    double A[MAXM], sA[MAXPP];
    all_areas(X,Y,A);
    double cur = amin(A);
    double step = 3e-3;
    static const double DX[8]={1,-1,0,0,0.70710678118654752,-0.70710678118654752,0.70710678118654752,-0.70710678118654752};
    static const double DY[8]={0,0,1,-1,0.70710678118654752,0.70710678118654752,-0.70710678118654752,-0.70710678118654752};
    int passes = 0;
    while (step > 1e-14 && passes < 20000){
        passes++;
        int improved = 0;
        for (int i = 0; i < N; i++){
            double r0 = sqrt(X[i]*X[i]+Y[i]*Y[i]);
            int onb = (r0 > 1.0 - 1e-13);
            for (int d = 0; d < 10; d++){
                double ox = X[i], oy = Y[i], nx, ny;
                if (d < 8){ nx = ox + step*DX[d]; ny = oy + step*DY[d]; }
                else {            /* slide along the boundary circle */
                    if (!onb) continue;
                    double th = atan2(oy,ox) + (d==8 ? step : -step);
                    nx = cos(th); ny = sin(th);
                }
                project(&nx,&ny);
                for (int k = 0; k < PPC; k++) sA[k] = A[PP[i][k]];
                X[i]=nx; Y[i]=ny;
                for (int k = 0; k < PPC; k++) A[PP[i][k]] = tri(X,Y,PP[i][k]);
                double cand = amin(A);
                if (cand > cur){ cur = cand; improved = 1; }
                else { X[i]=ox; Y[i]=oy; for (int k=0;k<PPC;k++) A[PP[i][k]] = sA[k]; }
            }
        }
        if (!improved) step *= 0.5;
    }
    return cur;
}

/* (1+1)-ES on ALL coordinates at once.  Coordinate-wise pattern search stalls at
   degenerate max-min points (e.g. the regular hexagon, where many triangles are
   simultaneously minimal and every single-point move is blocked); simultaneous
   moves get past that. */
static double polish_full(double *X, double *Y, RNG *rng){
    double A[MAXM], oX[MAXN], oY[MAXN];
    all_areas(X,Y,A);
    double cur = amin(A);
    double sigma = 1e-3;
    int fails = 0;
    for (long long it = 0; it < 400000 && sigma > 1e-16; it++){
        memcpy(oX,X,sizeof(double)*N); memcpy(oY,Y,sizeof(double)*N);
        for (int i = 0; i < N; i++){
            X[i] += sigma*rnorm(rng); Y[i] += sigma*rnorm(rng);
            project(&X[i], &Y[i]);
        }
        all_areas(X,Y,A);
        double cand = amin(A);
        if (cand > cur){ cur = cand; fails = 0; sigma *= 1.3; if (sigma > 1e-2) sigma = 1e-2; }
        else {
            memcpy(X,oX,sizeof(double)*N); memcpy(Y,oY,sizeof(double)*N);
            if (++fails >= 30){ fails = 0; sigma *= 0.7; }
        }
    }
    all_areas(X,Y,A);
    return amin(A);
}

/* ---------------- one restart ---------------- */
static double anneal(int r_index, long long iters, unsigned long long seed,
                     double *bestX, double *bestY){
    RNG rng; rseed(&rng, seed);
    double X[MAXN], Y[MAXN], A[MAXM], sA[MAXPP];

    /* deliberate seeding: cycle the number of boundary points over 3..N so that
       all-on-circle and (N-1)-on-circle-plus-centre are always covered. */
    int cyc = N - 2;
    int k = 3 + (r_index % cyc);
    int fam = r_index / cyc;
    double ang[MAXN];
    if (fam % 3 == 0) for (int i = 0; i < k; i++) ang[i] = 2*M_PI*i/k;     /* regular k-gon */
    else              for (int i = 0; i < k; i++) ang[i] = runif(&rng)*2*M_PI;
    for (int i=1;i<k;i++){ double v=ang[i]; int j=i-1; while(j>=0&&ang[j]>v){ang[j+1]=ang[j];j--;} ang[j+1]=v; }
    for (int i = 0; i < k; i++){ X[i]=cos(ang[i]); Y[i]=sin(ang[i]); }
    int inter = N - k;
    for (int i = 0; i < inter; i++){
        if (inter == 1 && (fam % 2 == 0)){ X[k]=0.0; Y[k]=0.0; }           /* exact centre seed */
        else {
            double th = runif(&rng)*2*M_PI, rad = sqrt(0.02+0.96*runif(&rng));
            X[k+i]=rad*cos(th); Y[k+i]=rad*sin(th);
        }
    }

    all_areas(X,Y,A);
    double cur = amin(A);
    double step = 0.10;
    long long decay = iters / 40; if (decay < 1) decay = 1;
    for (long long it = 0; it < iters; it++){
        double frac = 1.0 - (double)it/(double)iters;
        double T = 0.02*cur*frac*frac; if (T < 1e-15) T = 1e-15;
        int i = (int)(rnext(&rng) % (unsigned long long)N);
        double ox = X[i], oy = Y[i];
        for (int q = 0; q < PPC; q++) sA[q] = A[PP[i][q]];
        double nx = ox + step*rnorm(&rng), ny = oy + step*rnorm(&rng);
        project(&nx,&ny);
        X[i]=nx; Y[i]=ny;
        for (int q = 0; q < PPC; q++) A[PP[i][q]] = tri(X,Y,PP[i][q]);
        double cand = amin(A);
        if (cand > cur || runif(&rng) < exp((cand-cur)/T)) cur = cand;
        else { X[i]=ox; Y[i]=oy; for (int q=0;q<PPC;q++) A[PP[i][q]] = sA[q]; }
        if (it % decay == decay-1){ step *= 0.75; if (step < 1e-7) step = 1e-7; }
    }
    polish(X,Y);
    polish_full(X,Y,&rng);
    double v = polish(X,Y);              /* one more coordinate sweep to settle */
    memcpy(bestX,X,sizeof(double)*N); memcpy(bestY,Y,sizeof(double)*N);
    return v;
}

/* ---------------- threading ---------------- */
typedef struct {
    int lo, hi; long long iters; unsigned long long seed_base;
    double *vals; double *cfg;     /* cfg[r*2*MAXN + 2*i], [.. + 2*i+1] */
} Task;

static void *worker(void *p){
    Task *t = (Task*)p;
    double X[MAXN], Y[MAXN];
    for (int r = t->lo; r < t->hi; r++){
        double v = anneal(r, t->iters, t->seed_base + 1000003ULL*(unsigned long long)r, X, Y);
        t->vals[r] = v;
        double *dst = t->cfg + (size_t)r*2*MAXN;
        for (int i = 0; i < N; i++){ dst[2*i] = X[i]; dst[2*i+1] = Y[i]; }
    }
    return NULL;
}

int main(int argc, char **argv){
    if (argc < 6){ fprintf(stderr,"usage: heil n iters restarts threads seed_base\n"); return 2; }
    int n = atoi(argv[1]);
    long long iters = atoll(argv[2]);
    int restarts = atoi(argv[3]);
    int threads = atoi(argv[4]);
    unsigned long long seed_base = strtoull(argv[5],NULL,10);
    build_index(n);

    int topk = (argc > 6) ? atoi(argv[6]) : restarts;
    if (topk > restarts) topk = restarts;

    double *vals = (double*)calloc(restarts, sizeof(double));
    double *cfg  = (double*)calloc((size_t)restarts*2*MAXN, sizeof(double));
    pthread_t th[128]; Task tk[128];
    if (threads > 128) threads = 128;
    int chunk = (restarts + threads - 1)/threads;
    int nt = 0;
    for (int i = 0; i < threads; i++){
        int lo = i*chunk, hi = lo+chunk; if (hi > restarts) hi = restarts;
        if (lo >= hi) break;
        memset(&tk[nt], 0, sizeof(Task));
        tk[nt].lo = lo; tk[nt].hi = hi; tk[nt].iters = iters;
        tk[nt].seed_base = seed_base; tk[nt].vals = vals; tk[nt].cfg = cfg;
        pthread_create(&th[nt], NULL, worker, &tk[nt]); nt++;
    }
    for (int i = 0; i < nt; i++) pthread_join(th[i], NULL);

    /* emit the top-k restarts, best first: each gets an LP polish downstream */
    int *ord = (int*)malloc(sizeof(int)*restarts);
    for (int r = 0; r < restarts; r++) ord[r] = r;
    for (int a = 0; a < topk; a++){          /* partial selection sort */
        int bi = a;
        for (int b = a+1; b < restarts; b++) if (vals[ord[b]] > vals[ord[bi]]) bi = b;
        int tmp = ord[a]; ord[a] = ord[bi]; ord[bi] = tmp;
    }
    for (int a = 0; a < topk; a++){
        int r = ord[a];
        double *src = cfg + (size_t)r*2*MAXN;
        printf("%.17g", vals[r]);
        for (int i = 0; i < n; i++) printf(" %.17g %.17g", src[2*i], src[2*i+1]);
        printf("\n");
    }
    fprintf(stderr,"#n=%d restarts=%d emitted=%d best_pre_lp=%.12f\n",
            n, restarts, topk, vals[ord[0]]);
    return 0;
}
