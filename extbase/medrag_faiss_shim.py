"""Minimal stand-in for the `faiss` module, covering what MedRAG's utils.py uses.

Why: there is no faiss wheel for this cluster's Python (wheelhouse has none, PyPI's
compiled wheels are rejected) and building faiss needs swig + a C++ toolchain. MedRAG only
uses exact flat indexes (IndexFlatIP / IndexFlatL2; HNSW is opt-in and off here), so an
exact numpy implementation returns the SAME neighbours and scores as faiss's flat index.

Implements: IndexFlatIP, IndexFlatL2, IndexHNSWFlat (treated as flat = exact), the
METRIC_* constants, index.add / index.search / index.ntotal / index.d / index.metric_type,
write_index / read_index (stored as <path>.npy + <path>.json).
"""
import json
import os

import numpy as np

METRIC_INNER_PRODUCT = 0
METRIC_L2 = 1


class _Flat:
    def __init__(self, d, metric_type):
        self.d = int(d)
        self.metric_type = metric_type
        self._blocks = []
        self._x = None

    @property
    def ntotal(self):
        return 0 if self._x is None and not self._blocks else (
            self._x.shape[0] if self._x is not None else sum(b.shape[0] for b in self._blocks))

    def add(self, x):
        x = np.ascontiguousarray(np.asarray(x, dtype=np.float32))
        if x.ndim == 1:
            x = x[None, :]
        assert x.shape[1] == self.d, f"dim {x.shape[1]} != {self.d}"
        self._blocks.append(x)
        self._x = None

    def _mat(self):
        if self._x is None:
            self._x = np.concatenate(self._blocks, axis=0) if self._blocks else np.zeros((0, self.d), np.float32)
            self._blocks = [self._x]
        return self._x

    def search(self, q, k):
        q = np.ascontiguousarray(np.asarray(q, dtype=np.float32))
        if q.ndim == 1:
            q = q[None, :]
        X = self._mat()
        n = X.shape[0]
        k = int(min(k, n)) if n else 0
        if k == 0:
            return np.zeros((q.shape[0], 0), np.float32), np.zeros((q.shape[0], 0), np.int64)
        if self.metric_type == METRIC_INNER_PRODUCT:
            scores = q @ X.T                                   # higher is better
            idx = np.argpartition(-scores, k - 1, axis=1)[:, :k]
            part = np.take_along_axis(scores, idx, axis=1)
            order = np.argsort(-part, axis=1)
        else:                                                  # squared L2, lower is better
            scores = (q * q).sum(1)[:, None] - 2 * q @ X.T + (X * X).sum(1)[None, :]
            idx = np.argpartition(scores, k - 1, axis=1)[:, :k]
            part = np.take_along_axis(scores, idx, axis=1)
            order = np.argsort(part, axis=1)
        return (np.take_along_axis(part, order, axis=1).astype(np.float32),
                np.take_along_axis(idx, order, axis=1).astype(np.int64))


class IndexFlatIP(_Flat):
    def __init__(self, d):
        super().__init__(d, METRIC_INNER_PRODUCT)


class IndexFlatL2(_Flat):
    def __init__(self, d):
        super().__init__(d, METRIC_L2)


class IndexHNSWFlat(_Flat):
    """Exact search in place of HNSW (MedRAG constructs it only when HNSW=True)."""
    def __init__(self, d, M=32):
        super().__init__(d, METRIC_L2)


def write_index(index, path):
    np.save(path + ".npy", index._mat())
    with open(path + ".json", "w") as f:
        json.dump({"d": index.d, "metric_type": index.metric_type}, f)
    open(path, "w").close()                                    # the file MedRAG tests for


def read_index(path):
    with open(path + ".json") as f:
        meta = json.load(f)
    idx = IndexFlatIP(meta["d"]) if meta["metric_type"] == METRIC_INNER_PRODUCT else IndexFlatL2(meta["d"])
    idx.add(np.load(path + ".npy", mmap_mode=None))
    return idx
