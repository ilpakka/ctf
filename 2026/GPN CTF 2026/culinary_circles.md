# GPN CTF 2026 - Culinary Circles

## Overview

This was an osint task where I was given 9 images with files adam, alice, alkalem, beatrice, bob, bruno, carol, catherine and cristoph. From the name "Culinary **Circles**" and from the mention of OpenStreetMap I immediately recognized that it was going to be similar to UmassCTF osint (Where you were given images with radiuses and their circles intersection was the location that was used as a flag).

In this hovewer I was not given radiuses. Instead, I was given 9 images, 3 starting with a, 3 with b and 3 with c. After some thinking I realized that 3 points is all you need for circles. So I have to find all of those locations and make circles with 3 points from each letter and check the intersection of all of those circles.

## Locations

adam= https://maps.app.goo.gl/GCjp7nL9PaxdBaT6A 55.4567616, 12.1787524
Found by reverse image searching the hofu logo from the napkin and finding the restaurant's Facebook

alice=https://maps.app.goo.gl/PKxqdKXTvy75jicn8 52.8618045,-8.1982565
Found by looking for the location of "EBs Nenagh" that was seen on the reflection

alkalem=https://maps.app.goo.gl/HWW8MaXFhCbd2shh9 49.0073693, 8.4191435
Google reverse image search found the place instantly. Confirmed by comparing the signs and lamps to the images shown.

beatrice=https://maps.app.goo.gl/kgHktszMoyGA6KGA8 47.3226904, 5.0382642
Found french language, so searched for BCHEF:s in france that were also next to City Loft.

bob=https://maps.app.goo.gl/eAPBwCY7qUfRcEmBA 38.6972008, -9.2035704
Reverse image search and looking for exact matches found me the exact image with "Pasteis de Belem" logo. Searched for that restaurant.

bruno=https://maps.app.goo.gl/LUij7twhVASKoRdK8 51.9957398, 4.4755506
Trickiest one so far. Confirmed Netherlands instantly by searching for the outdoor toilet company. Saw on the ground the road name and came to the conclusion that it was "Westersingel". Then I went through every Westersingel in netherlands and found the correct location.

carol=https://maps.app.goo.gl/qXKcFGMSrw99NrWP8 59.3247366, 18.0763164
Reverse image search gave me similar looking venue. Went looking for that and found the same restaurant.

catherine=https://maps.app.goo.gl/QdcK4N2Z7T8e8KjJA 55.898451, -3.7025742
Reverse image searching gave me similar looking image from scotland. Navigated to a similar looking building from there that was seen in the bottom right of the original image and found the restaurant.

cristoph=https://maps.app.goo.gl/auh4iG1vvH4P3zAU9 54.899355, 9.7955834
Reverse image searching that with words "Mad kaffe" gave me the Cafe Marina facebook site.

## Final step

For the last step, I used ChatGPT to help me to get the circles in GeoJSON file. I used the following prompt:
"adam= https://maps.app.goo.gl/GCjp7nL9PaxdBaT6A
alice=https://maps.app.goo.gl/PKxqdKXTvy75jicn8
alkalem=https://maps.app.goo.gl/HWW8MaXFhCbd2shh9
beatrice=https://maps.app.goo.gl/kgHktszMoyGA6KGA8
bob=https://maps.app.goo.gl/eAPBwCY7qUfRcEmBA
bruno=https://maps.app.goo.gl/LUij7twhVASKoRdK8
carol=https://maps.app.goo.gl/qXKcFGMSrw99NrWP8
catherine=https://maps.app.goo.gl/QdcK4N2Z7T8e8KjJA
cristoph=https://maps.app.goo.gl/auh4iG1vvH4P3zAU9 Make points from ALl of the places coordinates that start with similar letter. You should get 3 circles with each containing 3 points. Use these circles radiuses to pinpoint one restaurant in openstreetmaps. Make GeoJSON circles file."

I got a GeoJSON file with one restaurant near the intersection pointed out: The Three Chimneys.

Flag: GPNCTF{The Three Chimneys}
