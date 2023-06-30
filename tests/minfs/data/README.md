# MinFS-py test data

This directory contains data for testing MinFS tools. This file describes how some of the files 
were created and how to recreate them.

## RegmapStructFile
File `4wire-params.bin`, `4wire-params.json`, `4wire-params-1.json`, `4wire-params-2.json`,
`4wire-params-incorrect.json` and `shared-cml-lib-regmap.json` are used to test the structure
packing feature. 

### 4wire-params.bin
4wire-params.bin contains a packed C structure that contains data identical to the data described
in `4wire-params.json` and `4wire-params-1.json`+`4wire-params-2.json` combined. It was created
using the following C++ code:

```c
CmlParams *params1;
FILE *fp;
fp = fopen("4wire-params.bin", "wb");
params1 = new CmlParams;

/* SCM */
params1->ssl_params.persist.pub.scm_params.scm_matrix_values[0] = 4096;
params1->ssl_params.persist.pub.scm_params.scm_matrix_values[1] = 0;
params1->ssl_params.persist.pub.scm_params.scm_matrix_values[2] = 0;
params1->ssl_params.persist.pub.scm_params.scm_matrix_values[3] = 4096;
params1->ssl_params.persist.pub.scm_params.scm_inverse_matrix_values[0] = 4096;
params1->ssl_params.persist.pub.scm_params.scm_inverse_matrix_values[1] = 0;
params1->ssl_params.persist.pub.scm_params.scm_inverse_matrix_values[2] = 0;
params1->ssl_params.persist.pub.scm_params.scm_inverse_matrix_values[3] = 4096;
   
/* btm_params */
params1->ssl_params.persist.prv.btm_params.btm_base = 81;
params1->ssl_params.persist.prv.btm_params.btm_win = 98;
params1->ssl_params.persist.prv.btm_params.btm_grad = -40;
params1->ssl_params.persist.prv.btm_params.btm_tempinit = 500;
params1->ssl_params.persist.prv.btm_params.btm_tempwd = 500;
params1->ssl_params.persist.prv.btm_params.btm_biasmax = 200;
params1->ssl_params.persist.prv.btm_params.btm_w_temp_max = 1500;

/* pwm_frequency */
params1->pwm_frequency = 2880093114;

/* tempest_params */
params1->ssl_params.persist.pub.tempest_params.tempest_offset = 11;
params1->ssl_params.persist.pub.tempest_params.tempest_grad = 12;

/* tv_params */
params1->ssl_params.persist.prv.tv_params.tv_errlim = 2222;

/* stm_params */
params1->ssl_params.persist.prv.stm_params.stm_base = 260;
params1->ssl_params.persist.prv.stm_params.stm_gradlow = 261;
params1->ssl_params.persist.prv.stm_params.stm_gradhigh = 1111;
params1->ssl_params.persist.prv.stm_params.stm_tempref = 222;

/* ffp_params_4w */
params1->ssl_params.persist.prv.ffp_params_4w.ffp_features = 1;
params1->ssl_params.persist.prv.ffp_params_4w.ffp_kprop[0] = 100;
params1->ssl_params.persist.prv.ffp_params_4w.ffp_kprop[1] = 250;

/* ffd_legacy_params */
params1->ssl_params.persist.prv.ffd_legacy_params.ffd_features = 1;
params1->ssl_params.persist.prv.ffd_legacy_params.ffd_kdyn[0] = 444;
params1->ssl_params.persist.prv.ffd_legacy_params.ffd_kdyn[1] = 231;
params1->ssl_params.persist.prv.ffd_legacy_params.ffd_tc[0] = 305;
params1->ssl_params.persist.prv.ffd_legacy_params.ffd_tc[1] = 212;

fwrite((uint8_t*)params1, sizeof(CmlParams), 1, fp);

fclose(fp);
```

Libraries that were used:
* shared_cml_library (git hash: 04d9abb931674a0da6b522b43c16ec548a213ed9)
* ssl (git hash: d57844ea92c5bf5bc2817d66c4923a4d5c9bff0f)

### 8wire-params.bin
8wire-params.bin contains a packed C structure that contains data identical to the data described
in `8wire-params.json`. It was created using the following C++ code:

```c
CmlParams *params1;
FILE *fp;
fp = fopen("8wire-params.bin", "wb");
params1 = new CmlParams;
   
/* btm_params */
params1->ssl_params.persist.prv.btm_params.btm_base = 81;
params1->ssl_params.persist.prv.btm_params.btm_win = 98;
params1->ssl_params.persist.prv.btm_params.btm_grad = -40;
params1->ssl_params.persist.prv.btm_params.btm_tempinit = 500;
params1->ssl_params.persist.prv.btm_params.btm_tempwd = 500;
params1->ssl_params.persist.prv.btm_params.btm_biasmax = 200;
params1->ssl_params.persist.prv.btm_params.btm_w_temp_max = 1500;

/* pwm_frequency */
params1->pwm_frequency = 2880093114;

/* Position gain correstion */
params1->ssl_params.persist.prv.pos_8w_params.pos_gain_correction[0] = 16466;
params1->ssl_params.persist.prv.pos_8w_params.pos_gain_correction[1] = 16302;
params1->ssl_params.persist.prv.pos_8w_params.pos_gain_correction[2] = 16465;
```

Libraries that were used:
* shared_cml_library (git hash: 2346a3dc80f9d02eff54a7ad2adc8a878069cb23)
* ssl (git hash: 6115c3aebdbb1b722af6b700b954291e3276b9e8)

### 2wire-params.bin
2wire-params.bin contains a packed C structure that contains data identical to the data described
in `2wire-params.json`. It was created using the following C++ code:

```c
CmlParams *params1;
FILE *fp;
fp = fopen("2wire-params.bin", "wb");
params1 = new CmlParams;
   
/* btm_params */
params1->ssl_params.persist.prv.btm_params.btm_base = 81;
params1->ssl_params.persist.prv.btm_params.btm_win = 98;
params1->ssl_params.persist.prv.btm_params.btm_grad = -40;
params1->ssl_params.persist.prv.btm_params.btm_tempinit = 500;
params1->ssl_params.persist.prv.btm_params.btm_tempwd = 500;
params1->ssl_params.persist.prv.btm_params.btm_biasmax = 200;
params1->ssl_params.persist.prv.btm_params.btm_w_temp_max = 1500;

/* pwm_frequency */
params1->pwm_frequency = 2880093114;

/* Demlim range*/
params1->ssl_params.persist.prv.demand_limit_2w_params.demlim_range_neg = 172;
params1->ssl_params.persist.prv.demand_limit_2w_params.demlim_range_pos = 173;
```

Libraries that were used:
* shared_cml_library (git hash: 2346a3dc80f9d02eff54a7ad2adc8a878069cb23)
* ssl (git hash: 6115c3aebdbb1b722af6b700b954291e3276b9e8)