This project is meant as a way for me to learn more about quantitative research aspect. This is most definitly for educational/research purposes only; not investment advice.

I do not own the data used for this project. All data come from the [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
and are copyright Eugene F. Fama and Kenneth R. French, who build them from CRSP and Compustat data.
The files in `data/1_zipped/` are unmodified copies, kept so the results can be reproduced exactly:
the library replaces its files at every update. They are not covered by this repository's MIT license, and I will remove them if asked.

202609 CRSP database
download date (2026-11-11)
French’s build date (2026-10-26)
The build date 2026-10-26 applies only to the four return files; Siccodes49 is dated 2020-01-08. the period covered is July 1926 to September 2026, with momentum starting in January 1927.


d1a3b0b9896e1e633ed2aa85e24ca144d7998f8ab2ff344e2379383ebeb7b836  data/1_zipped/49_Industry_Portfolios_CSV.zip
b9d36d571e968d71f7b03207e7fed6398554f953719b8c1bf3ee3ad8d00e7520  data/1_zipped/49_Industry_Portfolios_daily_CSV.zip
27ed60e5b2caa9ea334a261cddfa864a9926f6bf45e9677c95dfd835c5abb315  data/1_zipped/F-F_Momentum_Factor_CSV.zip
b03d39e4bb253dda0f14893db3b78e64b40b8d6549a0fc0fd4111dae84c98618  data/1_zipped/F-F_Research_Data_Factors_CSV.zip
36761b4009107e11cd15cff0eb75f8837ef49f024524b7378634629bf90905d5  data/1_zipped/Siccodes49.zip


References
- Fama, E. F., and K. R. French (1993). Common risk factors in the returns on stocks and bonds.
  *Journal of Financial Economics* 33(1), 3–56. (the 3 factors)
- Fama, E. F., and K. R. French (1997). Industry costs of equity.
  *Journal of Financial Economics* 43(2), 153–193. (the industry classification)
- Carhart, M. M. (1997). On persistence in mutual fund performance.
  *Journal of Finance* 52(1), 57–82. (the four-factor model that adds momentum)
- Fama, E. F., and K. R. French (2023). Production of U.S. Rm-Rf, SMB, and HML in the
  Fama-French Data Library. Chicago Booth Research Paper No. 23-22. (how the factors are built today)