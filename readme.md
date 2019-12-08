# VisLab

This GUI application is design to help analysts model and calibrate traffic on a fast, reliable and organized manner.
It's a work in progress, but the final product will be a .exe, and made on Python 3.6 with Tkinter for the GUI programming.

## Uses

Use to make sensitivity analysis and calibration on networks, single/multiparameter, and receive a report with the results. You can configure multiple 'experiments' to organize your work and test new ideias.

You can also automatically export the Sensitivity Analysis results to a Genetic Algorithm in-built to calibrate your network, or configure by yourself the calibration module.

## Requirements (.exe)

- Windows 10 64 bits;
- Active Vissim 11 installation.

## Requirements (.py)

- Python 3.6x;
- Pandas;
- Win32com;
- Statistics;
- Itertools;
- Subprocess;
- Matplotlib;
- Numpy;
- Scipy.

## Installation

Download the "VisLAB" folder to any place of your machine. Inside of that folder is a file named "vislab.exe". That is the gui's launcher. Inside of "resources" is two sqlite databases: "vislab.db" and "ga.db". The first one stores the sensitivity analysis results and configurations, while the second one stores all the data regarding the calibration process. It can be easily explored using DB Browser.
After that, you can add a shortcut in your desktop for quick acess.

NOTE: Separating the .exe of it's folder, changing name/deleting/relocating the databases and any content of /resources module will cause the program to crash.  

## How to use

NOTE: It can take a few seconds to load.

First of all, you need to have a Vissim license active on your computer/network, and start a COM server. To do this, open Vissim, go to Help > Start COM server. That will not work on student's version. After that, it's pretty straight foward. Soon I will be adding a more in depth tutorial with a study case of a signalized intersection.

## Support

If you need help, have a question, or a sugestion, please feel free to contact me on matheus.ferreira@det.ufc.br. I check my email every 5 minutes (_really need stop that_), so you will be answered :).

## Roadmap

Soon I will be adding a roadmap with some requested features.


## Contributing

The source code is open and free to modify and distribute, but we would be glad if you could credit us!. If you have any questions about the source code and its utilization, feel free to send me a email at matheus.ferreira@det.ufc.br.
