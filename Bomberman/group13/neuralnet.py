import numpy as np
from math import exp
import pickle

class NeuralNet:
    # takes in the sizes of the layers in list format
    # activation functions for each layer
    # derivatives of each activation function
    def __init__(self, sizes, activs, activ_derivs, alpha):
        self.weights = []
        for i in range(len(sizes)-1):
            cur_w = np.ndarray((sizes[i],sizes[i+1]))
            cur_w.fill(0)
            self.weights.append(cur_w)
        self.activs = activs
        self.activ_derivs = activ_derivs
        self.sizes = sizes
        self.alpha = alpha
    
    def randomize_weights(self):
        for w in self.weights:
            w[:] = np.reshape(np.random.rand(w.size), w.shape)
    
    def feed_forward(self, v_in):
        '''
        Feeds forward the neural network
        calculating the value it currently represents
        https://medium.com/@14prakash/back-propagation-is-very-simple-who-made-it-complicated-97b794c97e5c
        '''
        v = v_in
        for w, activ in zip(self.weights, self.activs):
            # matrix multiply
            v = np.matmul(v,w)
            # activation function
            for i in range(len(v)):
                v[i] = activ(v[i])
        return v
    
    def backpropogate(self, v_in, v_expected):
        '''
        Does a single backpropogation on the neural network
        Supervised Learning, slide 28
        '''
        # get the vector of forward propogated values
        # layer by layer, layed out in node order
        a = np.ndarray(sum(self.sizes))
        last_idx = self.sizes[0]
        a[0:last_idx] = v_in
        cur_v = v_in
        for l in range(len(self.sizes)-1):
            activ = np.vectorize(self.activs[l])
            cur_v = np.matmul(cur_v,self.weights[l])
            next_idx = last_idx + cur_v.size
            a[last_idx:next_idx] = activ(cur_v)
            last_idx = next_idx
        # go through all the layers in reverse order and
        # backpropogate, updating the weights along the way
        # output layer
        deltas = np.ndarray(sum(self.sizes))
        deltas.fill(0)
        for j in range(len(v_expected)):
            deriv = self.activ_derivs[-1]
            # calculate the node idx, in this case
            # since its the last layer it's all the other layers
            # summed up plus j
            node_idx = j + sum(self.sizes[:-1])
            # calculate derivative values in reference to this layer
            deltas[node_idx] = deriv(v_in[j]) * (v_expected[j] - a[node_idx])
        # other layers in reverse order
        for l in reversed(range(0,len(self.sizes)-1)):
            deriv = self.activ_derivs[l]
            # for each node in the layers
            for i in range(self.sizes[l]):
                w_sum = 0
                j_offset = sum(self.sizes[:-1])
                for j in range(len(v_expected)):
                    w_sum += self.weights[l][i][j] * deltas[j+j_offset]
                # calculate the offset from the position in the weights
                # to the node idx
                i_offset = sum(self.sizes[0:l])
                deltas[i+i_offset] = deriv(v_in[i]) * w_sum
        # update every weight in network using deltas
        for w in self.weights:
            for i in range(w.shape[0]):
                for j in range(w.shape[1]):
                    w[i][j] = w[i][j] + self.alpha * a[i] * deltas[j]

    def __str__(self):
        s = "NeuralNet:\n"
        for w in self.weights:
            s += str(w) + "\n\n"
        return s

def relu(x):
    return max(0, x)

# numerically stable sigmoid function
# https://stackoverflow.com/questions/36268077/overflow-math-range-error-for-log-or-exp
def sigmoid(gamma):
    if gamma < 0:
        return 1 - 1 / (1 + exp(gamma))
    return 1 / (1 + exp(-gamma))

def linear(x):
    return x

def sigmoid_deriv(x):
    return sigmoid(x) * (1 - sigmoid(x))

def relu_deriv(x):
    if x > 0:
        return 1
    return 0

def linear_deriv(x):
    return 1

if __name__ == "__main__":
    # tests
    n = NeuralNet([3,2,1],
        [relu,sigmoid,linear],
        [relu_deriv,sigmoid_deriv,linear_deriv],
        0.1)
    print(n)
    n.randomize_weights()
    print(n)
    v_in = np.asanyarray([1,1,1])
    v_exp = np.asanyarray([0.5])
    print("FF:", n.feed_forward(v_in))
    for _ in range(100):
        n.backpropogate(v_in,v_exp)
        print("After BP:", n)
        print("FF after BP:", n.feed_forward(v_in))