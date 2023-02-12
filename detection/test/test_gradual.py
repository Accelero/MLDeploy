import numpy as np
from skmultiflow.drift_detection.adwin import ADWIN
from skmultiflow.drift_detection import KSWIN
import matplotlib.pyplot as plt


def main():
    '''
    ADWIN(ADaptive WINdowing) is an adaptive sliding window algorithm for detecting change, and keeping
    updated statistics about a data stream. ADWIN allows algorithms not adapted for drifting data, to be
    resistant to this phenomenon.
    The general idea is to keep statistics from a window of variable size while detecting concept drift.
    The algorithm will decide the size of the window by cutting the statistics’ window at different points and
    analysing the average of some statistic over these two windows. If the absolute value of the difference
    between the two averages surpasses a pre-defined threshold, change is detected at that point and all data
    before that time is discarded.
    '''
    adwin = ADWIN()
    '''
    KSWIN (Kolmogorov-Smirnov Windowing) is a concept change detection method based on the 
    Kolmogorov-Smirnov (KS) statistical test. KS-test is a statistical test with no assumption of underlying data 
    distribution. KSWIN can monitor data or performance distributions. Note that the detector accepts one 
    dimensional input as array.
    KSWIN maintains a sliding window Ψ of fixed size n (window_size). The last r (stat_size) samples of Ψ are 
    assumed to represent the last concept considered as R. From the first n−r samples of Ψ, r samples are 
    uniformly drawn, representing an approximated last concept W.
    The KS-test is performed on the windows R and W of the same size. KS -test compares the distance of the 
    empirical cumulative data distribution dist(R,W).
    '''
    kswin = KSWIN(alpha=0.00001)

    # Construct a sinus signal dataset of length 2000.
    data_stream = np.sin(list(range(0, 2000)))

    for i in range(1100, 2000):
        data_stream[i] += 10

    # Oscillation interval represents the gradual drift.
    oscillationInterval = list(range(800, 820)) + list(range(830, 840)) + list(range(870, 940))\
                          + list(range(1000, 1030)) + list(range(1060, 1100))

    for i in oscillationInterval:
        data_stream[i] += 10

    # An empty list which will be used to store the drift points found by ADWIN.
    detected_adwin = []
    for i in range(2000):
        adwin.add_element(data_stream[i])
        if adwin.detected_change():
            print('Change detected in data : ' + str(data_stream[i]) + ' - at index: ' + str(i) + ' by adwin')
            detected_adwin.append(i)

    # An empty list which will be used to store the drift points found by KSWIN.
    detected_kswin = []
    for i in range(2000):
        kswin.add_element(data_stream[i])
        if kswin.detected_change():
            print('Change detected in data: ' + str(data_stream[i]) + ' - at index: ' + str(i) + ' by kswin')
            detected_kswin.append(i)

    # 'results' represents a weighted final result.
    # Drifts are detected, only when:
    # ADWIN + KSWIN (within a 'radius' wide scope) → Y
    # KSWIN → Y
    # ADWIN → N
    results = []
    radius = 20
    for i in detected_adwin:
        for k in detected_kswin:
            if abs(i - k) <= radius:
                results.append(i)
    results.extend(detected_kswin)
    # results.sort()
    for i in results:
        print(' Final results: at in index: ' + str(i))

    # Visualize the results.
    x = range(2000)
    y = data_stream
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)
    ax1.plot(x, y)
    for i in detected_adwin:
        ax1.axvline(i, color='red', ls='--')
    ax1.set_title('detection with ADWIN')

    ax2.plot(x, y)
    for i in detected_kswin:
        ax2.axvline(i, color='red', ls='--')
    ax2.set_title('detection with KSWIN')

    ax3.plot(x, y)
    for i in results:
        ax3.axvline(i, color='limegreen', ls='--')
    ax3.set_title('the final weighted result')

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
