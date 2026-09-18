# Family template for the arbitrary-size statement (blind-review input only)

The statement refers to an explicit constant $W_K(\eta)$ "of the appendix". You do not get the appendix.
You get only the SHAPE of the hard family below, with two unknowns (the truncation index $m$ and the
plateau slope $d$); your task includes deriving what $m$ and $d$ must satisfy for the family to be a legal
instance of Definition 1 with monotone submodular $f$, and the resulting value $W_K(\eta)=F(K,0)$.

Ground set $N=B\sqcup O$, $|O|=K$, $|B|=n-K$; for $S\subseteq N$ write $x=|S\cap B|$, $y=|S\cap O|$.
Parameters: $k_1=(K-1)\eta+1$, $q=(K-1)\eta/k_1$, $\nu=\eta/(\eta-1)$, an integer $j$ with
$0\le j\le K-1$ (the active segment index of $\rho_K=\min_j V_j$), $Q=q^{j}$, $C=k_1/K$,
$c_y=(K-y)/(K-1)$. Unknowns: an integer $m\ge1$ and a real $d>0$; put $D=Qd$ and $t^{\ast}=j+m$.

Sequences on integers $x\ge0$:
$$r_x=\begin{cases}q^{x},&x\le j,\\ Q-(x-j)D,&j<x\le t^{\ast},\\ 0,&x>t^{\ast},\end{cases}\qquad
g_x=\begin{cases}q^{x}/K,&x\le j,\\ \eta D-(\eta D-Q/K)\,\nu^{x-j},&j<x\le t^{\ast},\\ 0,&x>t^{\ast},\end{cases}$$
$a_x=r_x-g_x$. Objective and scaled surrogate ($H=\eta_u\tilde f$):
$$f(S)=F(x,y)=\begin{cases}1-r_x,&y=0,\\1-c_y\,a_x,&y\ge1,\end{cases}\qquad
H(x,y)=\begin{cases}C-r_x-(\eta-1)a_x,&y=0,\\ C-\eta\,c_y\,a_x,&y\ge1.\end{cases}$$

Tasks for the blind derivation: (1) find the condition on $(m,d)$ under which $F$ is monotone submodular,
$0\le F\le1$, $F(0,K)=1$, and the band $\Delta F\le\Delta H\le\eta\,\Delta F$ holds on every edge of the
count grid, including the closing step $x=t^{\ast}\to t^{\ast}+1$; (2) show that $H(x+1,0)=H(x,1)$ for
every $x$ (the surrogate depends only on $|S|$ whenever $|S\cap O|\le1$, at every size); (3) express
$W_K(\eta)=F(K,0)$ and $W_K-\rho_K$ in terms of $(m,d)$; (4) derive a criterion that selects an
admissible integer $m$ (a function $\Psi(t)$ whose first nonpositive integer point is $m$), the location
bounds on $m$ relative to $\eta(K-1)$ and $K\eta$, and the bound
$W_K-\rho_K<1/(K(e^{K-1}-K-1))$ for $K\ge3$; (5) sketch why an algorithm with $O(nK)$ queries of
arbitrary size cannot distinguish the hidden $O$ as $n\to\infty$ (which queries can leak, and the
probability bound), and why the $n\to\infty$ quantifier cannot be dropped.
