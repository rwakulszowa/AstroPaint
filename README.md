# AstroPaint

Astronomical Image Processor

The main goal of this project is to develop a system to process images taken by the Hubble Space Telescope and made publicly available on the project's site.
The first application of the system is to automate processing of space images via image filtration, using filtrs developed for this purpose, as well as to remove artifacts and combine data from multiple measurement devices into one resulting image.
Another function is to analyze the objects contained in the images and classify them for features typical for the analyzed object's type. As part of the project, methods of creating models of galaxies, nebulas and galaxy clusters will be developed.

## Usage
- go to <a href="http://www.cosmos.esa.int/web/hst" name="ESA Hubble Archive">ESA Hubble Archive</a> -> Main Search Interface
- select the target (for example - Einstein)
- pick 3 observations taken with different optical elements. NOTE: all images must contain an identical field of view
- run `python main.py <obs1> <obs2> <obs3> -i=<iterations>`, for example:
```
python main.py IBY111010 IBY110010 IBY110020 -i=5
```
The resulting images will be stored in `./temp`
