Random Fourier Features
====

Python module of random fourier features for support vector machines.
This python module needs scikit-learn as a backend of SVM solver.
Now this mpdule only has a module for classification (RandomFourierFeatures.SVC),
however I will provide other SVM functions soon.

## Requirement

- Python 3.6.6
- Numpy 1.13.3
- scikit-learn 0.19.1

## Usage

Before running sample code, you need to download and convert MNIST data by the following command:

    $ cd data
    $ python3 

Original MNIST data will be downloaded automatically and converted to .npy file.
After generating MNIST .npy files, run sample script by the following command:

    $ cd source
    $ ./run.sh download_and_convert_mnist.py

This script run both of kernel SVM and SVM with RFF for MNIST data.
Results of these methods are logged and log files are stored in etc/ directory.

## Results of RFF and ORF

In my computing environment (CPU: Intl Core i5 5250U, RAM: 4GB), I got the following results:

<p align="center">
|Method|Training time (sec)|Prediction time (us)|Score (%)|
|:---:|:---:|:---:|:---:|
|Kernel SVM|214.2 sec|5837.4 us|96.3 %|
|SVM w/ RFF <br> d = 128|136.6 sec|21.3 us|93.4 %|
|SVM w/ ORF <br> d = 128|138.2 sec|21.4 us|93.4 %|
</p>

Learning time on RFF and ORF is faster than kernel SVM, moreover, prediction time of RFF and ORF is amazingly faster!

## Results of Batch RFF

I implemented a code for RFF SVM with batch learning and evaluate its accuracy on MNIST dataset.
I've got the following results. Learning time is even longer than usual kernel SVM.
However, accuracy is same as usual kernel SVM and, moreover, prediction time is much faster than usual kernel SVM.

<p align="center">
|Method|Training time (sec)|Prediction time (us)|Score (%)|
|:---:|:---:|:---:|:---:|
|SVM w/ batch RFF <br> d = 1024|2062.2 sec|108.6 us|96.4 %|
</p>

<p align="center">
![Accuracy for each epochs in SVM with batch RFF](./etc/output_main_rff_batch_plot.png)
</p>

## Licence

[MIT Licence](https://opensource.org/licenses/mit-license.php)

## Reference

[1] A. Rahimi and B. Recht, "Random Features for Large-Scale Kernel Machines", NIPS, 2007.
[PDF](https://papers.nips.cc/paper/3182-random-features-for-large-scale-kernel-machines.pdf)

## Author

Tetsuya Ishikawa (https://github.com/tiskw)

