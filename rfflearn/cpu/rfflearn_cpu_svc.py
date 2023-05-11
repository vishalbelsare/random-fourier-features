"""
Python module of support vector classification with random matrix for CPU.
"""

import numpy as np
import sklearn.svm
import sklearn.multiclass

from .rfflearn_cpu_common import Base


class SVC(Base):
    """
    Support vector classification with random matrix (RFF/ORF).
    """
    def __init__(self, rand_type, dim_kernel=128, std_kernel=0.1, W=None, b=None, multi_mode="ovr", n_jobs=-1, **args):
        """
        Constractor. Save hyper parameters as member variables and create LinearSVC instance.
        The LinearSVC instance is always wrappered by multiclass classifier.

        Args:
            rand_type  (str)       : Type of random matrix ("rff", "orf", "qrf", etc).
            dim_kernel (int)       : Dimension of the random matrix.
            std_kernel (float)     : Standard deviation of the random matrix.
            W          (np.ndarray): Random matrix for the input `X`. If None then generated automatically.
            b          (np.ndarray): Random bias for the input `X`. If None then generated automatically.
            multi_mode (str)       : Treatment of multi-class ("ovr" or "ovo").
            n_jobs     (int)       : The number of jobs to run in parallel.
            args       (dict)      : Extra arguments. This will be passed to sklearn's LinearSVC class constructor.
        """
        super().__init__(rand_type, dim_kernel, std_kernel, W, b)
        self.svm = self.set_classifier(sklearn.svm.LinearSVC(**args), multi_mode, n_jobs)

    def set_classifier(self, svm, multi_mode, n_jobs):
        """
        Select multiclass classifire. Now this function can handle one-vs-one and one-vs-others.

        Args:
            svm        (sklearn.svm.LinearSVC): Sklearn's LinnearSVC instance.
            multi_mode (str)                  : Treatment of multi-class ("ovr" or "ovo").
            n_jobs     (int)                  :

        Returns:
            (sklearn.base.BaseEstimator): Multi-class classifier instance.
        """
        if   multi_mode == "ovo": classifier = sklearn.multiclass.OneVsOneClassifier
        elif multi_mode == "ovr": classifier = sklearn.multiclass.OneVsRestClassifier
        else                    : classifier = sklearn.multiclass.OneVsRestClassifier
        return classifier(svm, n_jobs = n_jobs)

    def fit(self, X, y, **args):
        """
        Run training, that is, extract feature vectors and train SVC.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y    (np.ndarray): Output vector with shape (n_samples,).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `fit` function.

        Returns:
            (rfflearn.cpu.SVC): Myself.
        """
        self.set_weight(X.shape[1])
        self.svm.fit(self.conv(X), y, **args)
        return self

    def predict_proba(self, X, **args):
        """
        Return predicted probability for each target classes.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `predict_proba` function.

        Returns:
            (np.ndarray): Probability of each class.
        """
        self.set_weight(X.shape[1])
        return self.svm.predict_proba(self.conv(X), **args)

    def predict_log_proba(self, X, **args):
        """
        Return predicted log-probability for each target classes.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `predict_log_proba` function.

        Returns:
            (np.ndarray): Log probability of each class.
        """
        self.set_weight(X.shape[1])
        return self.svm.predict_log_proba(self.conv(X), **args)

    def predict(self, X, **args):
        """
        Return prediction results.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `predict_log_proba` function.

        Returns:
            (np.ndarray): Predicted classes.
        """
        self.set_weight(X.shape[1])
        return self.svm.predict(self.conv(X), **args)

    def score(self, X, y, **args):
        """
        Return evaluation score (classification accuracy).

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y    (np.ndarray): Output vector with shape (n_samples,).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `score` function.

        Returns:
            (float): Classification accyracy.
        """
        self.set_weight(X.shape[1])
        return self.svm.score(self.conv(X), y, **args)


class BatchSVC:
    """
    Batch training extention of the support vector classification.
    """
    def __init__(self, rand_type, dim_kernel, std_kernel, num_epochs=10, num_batches=10, alpha=0.05):
        """
        Constractor. Save hyper parameters as member variables and create LinearSVC instance.
        The LinearSVC instance is always wrappered by multiclass classifier.

        Args:
            rand_type   (str)  : Type of random matrix ("rff", "orf", "qrf", etc).
            dim_kernel  (int)  : Dimension of the random matrix.
            std_kernel  (float): Standard deviation of the random matrix.
            num_epochs  (int)  : Number of epochs to train.
            num_batches (int)  : Number of batches in one epoch.
            alpha       (float): Exponential moving average of each batch.
        """
        self.rtype   = rand_type
        self.coef    = None
        self.icpt    = None
        self.W       = None
        self.b       = None
        self.dim     = dim_kernel
        self.std     = std_kernel
        self.n_epoch = num_epochs
        self.n_batch = num_batches
        self.alpha   = alpha

    def shuffle(self, X, y):
        """
        Shuffle the order of the training data.

        Args:
            X (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y (np.ndarray): Output vector with shape (n_samples,).

        Retuens:
            (tuple): Tuple of shuffled X and y.
        """
        data_all = np.array(np.bmat([X, y.reshape((y.size, 1))]))
        np.random.shuffle(X)
        return (data_all[:, :-1], np.ravel(data_all[:, -1]))

    def train_batch(self, X, y, test, **args):
        """
        Train only one batch. This function will be called from the `fit` function.

        Args:
            X (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y (np.ndarray): Output vector with shape (n_samples,).
        """
        # Create classifier instance
        if   self.rtype == "rff": svc = RFFSVC(self.dim, self.std, self.W, **args)
        elif self.rtype == "orf": svc = ORFSVC(self.dim, self.std, self.W, **args)
        else                    : raise RuntimeError("BatchSVC: 'rand_type' must be 'rff' or 'orf'.")

        # Train SVM with random fourier features
        svc.fit(X, y)

        # Update coefficients of linear SVM
        coef = np.array([estimator.coef_.flatten() for estimator in svc.svm.estimators_])
        if self.coef is None: self.coef = coef
        else                : self.coef = self.alpha * coef + (1 - self.alpha) * self.coef

        # Update intercept of linear SVM
        icpt = np.array([estimator.intercept_.flatten() for estimator in svc.svm.estimators_])
        if self.icpt is None: self.icpt = icpt
        else                : self.icpt = self.alpha * icpt + (1 - self.alpha) * self.icpt

        # Keep random matrices of RFF/ORF
        if self.W is None: self.W = svc.W
        if self.b is None: self.b = svc.b

    def fit(self, X, y, test=None, **args):
        """
        Run training.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y    (np.ndarray): Output vector with shape (n_samples,).
            test (Tuple)     : Tuple of test data (X_test, y_test). If None, test will be skipped.

        Retuens:
            (rfflearn.cpu.BatchSVC): Myself.
        """
        # Calculate batch size
        batch_size = X.shape[0] // self.n_batch

        # Start training
        for epoch in range(self.n_epoch):

            # Shuffle training data.
            X, y = self.shuffle(X, y)

            for batch in range(self.n_batch):

                # Compute start/end index of batch.
                index_bgn = batch_size * (batch + 0)
                index_end = batch_size * (batch + 1)

                # Train one batch.
                self.train_batch(X[index_bgn:index_end, :], y[index_bgn:index_end], test, **args)

                # Print test score if specified.
                if test is not None:
                    print("Epoch = %d, Batch = %d, Accuracy = %.2f [%%]" % (epoch, batch, 100.0 * self.score(test[0], test[1], **args)))

        return self

    def predict(self, X, **args):
        """
        Return prediction results.

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `predict` function.

        Returns:
            (np.ndarray): 
        """
        svc = RFFSVC(self.dim, self.std, self.W, self.b, **args)
        return np.argmax(np.dot(svc.conv(X), self.coef.T) + self.icpt.flatten(), axis = 1)

    def score(self, X, y, **args):
        """
        Return evaluation score (classification accuracy).

        Args:
            X    (np.ndarray): Input matrix with shape (n_samples, n_features_input).
            y    (np.ndarray): Output vector with shape (n_samples,).
            args (dict)      : Extra arguments. This arguments will be passed to sklearn's `score` function.

        Returns:
            (float): Classification accyracy.
        """
        pred = self.predict(X)
        return np.mean([(1 if pred[n] == y[n] else 0) for n in range(X.shape[0])])


# The above functions/classes are not visible from users of this library, becasue the usage of
# the function is a bit complicated. The following classes are simplified version of the above
# classes. The following classes are visible from users.


class RFFSVC(SVC):
    """
    Support vector machine with RFF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("rff", *pargs, **kwargs)


class ORFSVC(SVC):
    """
    Support vector machine with ORF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("orf", *pargs, **kwargs)


class QRFSVC(SVC):
    """
    Support vector machine with QRF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("qrf", *pargs, **kwargs)


class RFFBatchSVC(BatchSVC):
    """
    Support vector machine with RFF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("rff", *pargs, **kwargs)


class ORFBatchSVC(BatchSVC):
    """
    Support vector machine with ORF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("orf", *pargs, **kwargs)


class QRFBatchSVC(BatchSVC):
    """
    Support vector machine with QRF.
    """
    def __init__(self, *pargs, **kwargs):
        super().__init__("qrf", *pargs, **kwargs)


# Author: Tetsuya Ishikawa <tiskw111@gmail.com>
# vim: expandtab tabstop=4 shiftwidth=4 fdm=marker
