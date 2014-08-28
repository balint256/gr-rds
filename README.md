### Dependencies

GNU Radio v3.7.

packets from your packet manager:
```
sudo apt-get install cmake libboost-all-dev libcppunit-dev liblog4cpp5-dev swig
```


### Installation

```
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig
```


### Usage

open apps/rds_rx.grc example flow graph in GNU Radio Companion.


### Demos

Quick example:
http://www.youtube.com/watch?v=05i9C5lhorY

HAK5 episode (including installation):
http://www.youtube.com/watch?v=ukhrIl4JHbw


### History

Continuation of gr-rds on BitBucket (originally from Dimitrios Symeonidis https://bitbucket.org/azimout/gr-rds/ and also on CGRAN https://www.cgran.org/wiki/RDS).
