import numpy as np
from collections import Counter

# euclidean distance
def euclidean_distance(x, y):
    x2 = np.sum(x*x, axis=1, keepdims=True)
    y2 = np.sum(y*y, axis=1, keepdims=True)
    return np.sqrt(np.maximum(x2 + y2.T - 2 * x @ y.T, 0.0))

# cosine distance
def one_minus_cosine_similarity(x, y, eps=1e-12):
    xn = x / (np.linalg.norm(x, axis=1, keepdims=True) + eps)
    yn = y / (np.linalg.norm(y, axis=1, keepdims=True) + eps)
    cos = np.clip(xn @ yn.T, -1.0, 1.0)
    return 1 - cos

# jaccard distance
def one_minus_jaccard_similarity(x, y, eps=1e-12):
    intersection = np.minimum(
        x[:, None, :], y[None, :, :]
    ).sum(axis=2)
    union = np.maximum(
        x[:, None, :], y[None, :, :]
    ).sum(axis=2) + eps
    return 1 - (intersection / union)

# sse computation
def sse(X, C, labels, dist_fn):
    D = dist_fn(X, C)
    return float(np.sum(D[np.arange(X.shape[0]), labels] ** 2))

# majority vote accuracy
def majority_vote_accuracy(labels_pred, y_true):
    mapping = {}
    for k in np.unique(labels_pred):
        idx = (labels_pred == k)
        mapping[k] = Counter(y_true[idx]).most_common(1)[0][0]
    y_hat = np.vectorize(mapping.get)(labels_pred)
    return float(np.mean(y_hat == y_true))

# KMEANS
def kmeans(X, k, dist_fn,
           max_iter=500, tol=1e-4,
           stop_mode="no_centroid_change",
           random_state=42):

    rng = np.random.default_rng(random_state)
    n, d = X.shape

    # k-means initialization using correct distance
    C = np.empty((k, d))
    idx0 = rng.integers(0, n)
    C[0] = X[idx0]

    D0 = dist_fn(X, C[None, 0, :])[:, 0]
    dist_vals = D0.copy()

    for i in range(1, k):
        probs = dist_vals / (dist_vals.sum() + 1e-12)
        idx = rng.choice(n, p=probs)
        C[i] = X[idx]

        Di = dist_fn(X, C[None, i, :])[:, 0]
        dist_vals = np.minimum(dist_vals, Di)

    # iterations
    history_sse = []
    prev_sse = None

    for it in range(max_iter):

        # assign labels
        D = dist_fn(X, C)
        labels = np.argmin(D, axis=1)

        # update centroids
        C_new = np.zeros_like(C)
        for j in range(k):
            pts = X[labels == j]
            if len(pts) == 0:
                C_new[j] = X[rng.integers(0, n)]
            else:
                C_new[j] = pts.mean(axis=0)

        # compute SSE
        cur_sse = sse(X, C_new, labels, dist_fn)
        history_sse.append(cur_sse)

        # stopping modes
        if stop_mode == "no_centroid_change":
            if np.allclose(C_new, C, atol=tol):
                C = C_new
                break
        # elif stop_mode == "sse_convergence":
        elif stop_mode == "sse_increase":
            if prev_sse is not None and cur_sse > prev_sse:
                break
         
        elif stop_mode == "max_iter":
            pass

        prev_sse = cur_sse
        C = C_new

    # final assignment
    D = dist_fn(X, C)
    labels = np.argmin(D, axis=1)
    return C, labels, history_sse

# kmean results saving
def save_kmean_results(metric_name, sse, accuracy, iterations, file_path=None):
    if file_path is None:
        file_path = f"../results/kmean/{metric_name}_results.txt"
    
    with open(file_path, "w") as f:
        f.write(f"kmeans results ({metric_name})\n")
        f.write("-" * 40 + "\n")
        f.write(f"final SSE: {sse}\n")
        f.write(f"accuracy: {accuracy}\n")
        f.write(f"iterations: {iterations}\n")
    
    print(f"Done saved: {file_path}")
