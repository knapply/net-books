# Sampson's novices: groups

One attribute for the 18 novices of the `sampson` data set: the group Sampson
assigned each to. Join to `../sampson/nodes.csv` on `name`.

## Files

`nodes.csv` (18 rows):

| column | meaning |
|---|---|
| `name` | the novice's name, spelled as in `../sampson/nodes.csv` |
| `group` | `Turks` (7: the Young Turks), `Loyal` (5: the Loyal Opposition), `Outcasts` (3), `Waverers` (3: the interstitial group) |

## Source

Copied from the `group` vertex attribute of the `samplk3` network in the
`statnet.data` package (https://github.com/statnet/statnet.data, commit
`6272770a5d77435e8fe0ad759a0a3a8461776ead`), which documents it as the groups
"as classified by Sampson". The vertex order there matches the `number` column
of `../sampson/nodes.csv` (one spelling differs: `Romauld` there, `Romuald`
here). The statnet.data package is licensed CC BY 4.0. The four groups are
those of Sampson (1968) and Breiger, Boorman and Arabie (1975); the fourth is
called the interstitial group in the Pajek description of these data.

## Citation

Sampson, S. F. (1968). *A Novitiate in a Period of Change: An Experimental
and Case Study of Social Relationships*. PhD dissertation, Cornell
University.

The Statnet Project. *statnet.data: Data Sets for the Statnet Suite of
Packages*. https://statnet.org
