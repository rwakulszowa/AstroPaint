# AstroPaint

Astronomical Image Processor

The main goal of this project is to develop a system to process images taken by the Hubble Space Telescope and made publicly available on the project's site.
The first application of the system is to automate processing of space images via image filtration, using filtrs developed for this purpose, as well as to remove artifacts and combine data from multiple measurement devices into one resulting image.
Another function is to analyze the objects contained in the images and classify them for features typical for the analyzed object's type. As part of the project, methods of creating models of galaxies, nebulas and galaxy clusters will be developed.

## Usage
- go to <a href="http://www.cosmos.esa.int/web/hst" name="ESA Hubble Archive">ESA Hubble Archive</a> -> Main Search Interface 
- select the target (for example - Einstein)
- pick 3 observations taken with different optical elements. NOTE: all images must contain an identical field of view
- copy a link to a DRZ file for each observation, i.e. for `Observation ID = IC3U13080`, the link would be
```
http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID=IC3U13080_DRZ
```
- run `python3 main.py <link1> <link2> <link3>`, for example:
```
python3 main.py "http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID=IC3U13040_DRZ" "http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID=IC3U13080_DRZ" "http://archives.esac.esa.int/ehst-sl-server/servlet/data-action?RETRIEVAL_TYPE=PRODUCT&ARTIFACT_ID=IC3U12080_DRZ"
```
The resulting image will be stored in `./temp`
