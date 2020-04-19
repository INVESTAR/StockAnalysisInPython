import numpy as np
X = np.array([10, 20])  # ①
W1 = np.array([[0.1, 0.3, 0.5], [0.2, 0.4, 0.6]])
B1 = np.array([1, 2, 3])  # ③

def sigmoid(x): 
    return 1 / (1 + np.exp(-x))

A1 = np.dot(X, W1) + B1
Z1 = sigmoid(A1)

print('A1 :', A1)
print('Z1 :', Z1)