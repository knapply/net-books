# Spatial networks (chapter: Networks in space)

Two small networks with places.

## borders/ : country land borders (real)

One-mode, undirected. 177 country units and the 313 pairs that share a land border.

- `nodes.csv`: `id` (Natural Earth `ADM0_A3` code), `name`, `continent`, `population`, `longitude`, `latitude`.
  The location is Natural Earth's label point for the unit (`LABEL_X`, `LABEL_Y`), WGS 84. It is where the
  name is printed on the map, not a true centroid. France's point is in Paris although the unit includes
  French Guiana.
- `edges.csv`: `source`, `target`, `border_km` (length of the shared border in the generalized 1:110m geometry).
- `geometry.csv`: the shared borders as WKT `MULTILINESTRING` in longitude and latitude, used only to draw the map.

Source: Natural Earth, Admin 0 - Countries, 1:110m cultural vectors, version 5.2.0-pre (2022), through the
tables bundled with the knappnet R package (`inst/extdata/country_borders`, built from
https://github.com/nvkelso/natural-earth-vector, commit ca96624a56bd078437bca8184e78163e5039ad19).
Licence: public domain (https://www.naturalearthdata.com/about/terms-of-use/).
Citation: Natural Earth. Admin 0 - Countries, 1:110m cultural vectors, version 5.2.0-pre (2022). Made with
Natural Earth, free vector and raster map data at naturalearthdata.com.
This copy keeps the columns the chapter uses and renames `code` to `id`, `from`/`to` to `source`/`target`.

## towns/ : commuters between twelve towns (INVENTED)

Not real data. Twelve made-up towns on a 100 km by 100 km square, planar coordinates in kilometers, with
populations in thousands, and the daily commuters between every pair.

- `nodes.csv`: `id`, `x_km`, `y_km`, `population_thousands`.
- `edges.csv`: `source`, `target`, `commuters`, undirected.

Commuters were generated as round(80 * P_i * P_j / d^2 * exp(e)), where P is population in thousands, d the
distance in km and e normal noise with standard deviation 0.35 (Python `random.seed(14)`, pairs in town
order, `random.gauss`), so the data follow a gravity law with exponent 2 plus noise. Released under the
book's licence; no real place is meant.
