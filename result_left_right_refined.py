

import sys
import traceback
import json
# reload(sys)
# sys.setdefaultencoding('utf-8');


import os
import pandas as pd
import numpy as np
from ppg import BASE_DIR
from functools import reduce
from ppg.utils import exist, load_json, dump_json, load_model, dump_model

import logging
from logging.handlers import TimedRotatingFileHandler
import ppg.utils as utils
Logger = utils.init_log_env()
# BASE_DIR = 'C:/Project/biomedix_py37_copy1'




def result_left():

    aggregated_dir = os.path.join(BASE_DIR, 'data', 'aggregated')
    model_dir = os.path.join(BASE_DIR, 'data', 'models')
    result_data_dir = os.path.join(BASE_DIR, 'data', 'result')
    # print(aggregated_dir)
    if exist(pathname=aggregated_dir):
        if exist(pathname=os.path.join(aggregated_dir, '%s.csv' % 'agg_left')):
            agg_left = pd.read_csv(os.path.join(aggregated_dir, '%s.csv' % 'agg_left'), encoding='utf-8')
            agg_left = agg_left.drop('Unnamed: 0', axis=1)
            left_toe_lab = agg_left[agg_left['m_point'] == 'Left toe'].drop('m_point', axis=1).dropna().reset_index(
                drop=True)

            if len(left_toe_lab) > 0:

                df1 = left_toe_lab.replace(np.inf, 1).fillna(0)
                #  logistic regression on left toe
                lr_data1 = pd.DataFrame()
                lr_data1['ID'] = df1['ID']
                df_vars1 = ['var_38', 'var_35', 'var_40', 'var_36', 'var_5', 'var_17', 'var_24',
                           'var_53', 'var_19', 'var_30', 'var_29', 'var_2', 'var_16', 'var_50',
                           'var_28', 'var_14', 'var_9', 'var_48', 'var_27', 'var_4', 'var_44',
                           'var_49', 'var_47', 'var_59', 'var_43', 'var_22', 'var_45', 'var_39',
                           'var_1', 'var_26', 'var_13', 'var_15', 'var_18']
                lr_data1[df_vars1] = df1[df_vars1]

                df_mean1 = np.array([-6.08217295e-02, 1.02210034e-01, 2.44276169e-01, -7.61828656e-01,
                                     -3.24879590e-03, 2.45043037e+03, 3.49175947e-01, 1.28969052e+00,
                                     1.45077745e-01, 2.39897302e-01, -4.87075016e-01, -9.25405016e+01,
                                     -7.23812652e+02, -2.30888096e-02, 5.16507260e+03, 2.42092624e-02,
                                     5.32071269e-01, 2.83393730e-01, -3.70316512e+04, 9.17004454e-01,
                                     4.85893951e-01, -3.12893794e-01, 6.01208389e-01, 1.05544960e+00,
                                     2.56497165e-01, 2.28262806e-01, 3.86728279e-01, 5.39643653e-01,
                                     5.48951217e+03, 6.20172564e+04, 1.00233853e-01, 1.13698897e+04,
                                     6.03974283e-01])
                df_std1 = np.array([5.05461098e-01, 2.65916946e-01, 2.42733321e-01, 1.35401404e+00,
                                   1.17458800e-01, 6.88834794e+03, 2.23396015e-01, 8.38606800e-01,
                                   2.72800016e-01, 3.37715170e-01, 8.17885839e-01, 5.08016107e+02,
                                   3.81488681e+03, 1.74342382e-01, 1.90090210e+04, 8.29190541e-01,
                                   2.14376257e-01, 2.70965991e-01, 1.65457464e+05, 3.74270027e-01,
                                   1.88645266e-01, 3.03673610e-01, 2.93833775e-01, 1.89330424e-01,
                                   1.62307751e-01, 1.73137528e-01, 2.28294403e-01, 3.56214298e-01,
                                   1.53656322e+04, 2.92561222e+05, 3.78692054e-02, 3.55217574e+04,
                                   1.35797177e-01])

                for i in range(len(df_mean1)):
                    lr_data1[df_vars1[i]] = (((lr_data1[df_vars1[i]]) - (df_mean1)[i]) / df_std1[i])
                # print(lr_data1)
                x_test1 = lr_data1.iloc[:, 1:]
                model_pathname1 = os.path.join(model_dir, '%s.model' % 'rf_left')
                rf_left = load_model(pathname=model_pathname1)
                y_pred1 = np.where(rf_left.predict_proba(x_test1)[:, 1] > 0.4595, 1, 0)

                lr_data1['Left_Y'] = y_pred1
                lr_data1['Left_Y'] = ['Normal' if x == 0 else 'Abnormal' for x in lr_data1['Left_Y']]
                # lr_data1['Left_prob'] = [x if x > 0.53268 else 1 - x for x in logreg_left.predict_proba(x_test1)[:, 1]]

                #  linear regression on left toe
                lr_data1_reg = pd.DataFrame()
                lr_data1_reg['ID'] = df1['ID']
                df_vars1_reg = ['var_26', 'var_29', 'var_6', 'var_5', 'var_23', 'var_30']
                lr_data1_reg[df_vars1_reg] = df1[df_vars1_reg]

                df_mean1_reg = np.array(
                    [5.20751933e+04, -4.41280678e-01, 1.02117981e+00, -2.11798077e-02, 3.84937888e-01, 6.57295788e-02])
                df_std1_reg = np.array(
                    [5.15260702e+04, 4.62709651e-01, 1.89986184e-01, 1.89986184e-01, 1.59067535e-01, 3.36380650e-01])

                for i in range(len(df_mean1_reg)):
                    lr_data1_reg[df_vars1_reg[i]] = (
                                ((lr_data1_reg[df_vars1_reg[i]]) - (df_mean1_reg)[i]) / df_std1_reg[i])

                lr_data1_reg.to_csv(  'left_reg_data_test1.csv', index=False)
                x_test1_reg = lr_data1_reg.iloc[:, 1:]
                model_pathname1_reg = os.path.join(model_dir, '%s.model' % 'reg_left')
                reg_left = load_model(pathname=model_pathname1_reg)
                # print(reg_left.coef_)
                # print(reg_left.intercept_)
                y_pred1_reg = reg_left.predict(x_test1_reg)
                lr_data1_reg['Left_ABI'] = y_pred1_reg



        if exist(pathname=os.path.join(aggregated_dir, '%s.csv' % 'agg_right')):

            agg_right = pd.read_csv(os.path.join(aggregated_dir, '%s.csv' % 'agg_right'), encoding='utf-8')
            agg_right = agg_right.drop('Unnamed: 0', axis=1)
            right_toe_lab = agg_right[agg_right['m_point'] == 'Right toe'].drop('m_point', axis=1).dropna().reset_index(
                drop=True)
            # print(agg_right)

            if len(right_toe_lab) > 0:
                df2 = right_toe_lab.replace(np.inf, 1).fillna(0)
                lr_data2 = pd.DataFrame()
                lr_data2['ID'] = df2['ID']
                df_vars2 = ['var_27', 'var_55', 'var_42', 'var_1', 'var_4', 'var_13', 'var_32',
                           'var_36', 'var_34', 'var_22', 'var_35', 'var_47', 'var_26', 'var_41',
                           'var_33', 'var_24', 'var_49', 'var_29', 'var_28', 'var_50', 'var_38',
                           'var_31', 'var_45', 'var_44', 'var_14', 'var_18', 'var_43']
                lr_data2[df_vars2] = df2[df_vars2]

                df_mean2 = np.array([-5.54296615e+04,  2.95121702e+00,  1.30293506e+05,  7.84941010e+03,
                                    9.11792237e-01,  1.00433790e-01,  1.01201240e+06, -7.06669667e-01,
                                   -5.74633485e+03,  2.29018265e-01,  1.16140412e-01,  5.84671576e-01,
                                    8.96685689e+04,  6.18009198e+04,  1.11117333e+04,  3.38561644e-01,
                                   -2.90898063e-01, -5.67802050e-01,  4.97560012e+03, -5.32984847e-03,
                                   -3.13355986e-02,  7.37060047e+05,  3.80830306e-01,  4.97615870e-01,
                                    3.05969337e-01,  5.93185773e-01,  2.59278293e-01])

                df_std2 = np.array([3.07929851e+05, 8.55215264e-01, 4.40379048e+05, 3.30981878e+04,
                                   3.54197331e-01, 4.08812061e-02, 5.16439774e+06, 1.34200668e+00,
                                   2.58235031e+04, 1.85035032e-01, 2.78407721e-01, 3.03430877e-01,
                                   4.23320710e+05, 5.45606322e+05, 5.21530157e+04, 2.17652711e-01,
                                   3.04183274e-01, 8.62012264e-01, 2.58618437e+04, 1.75244090e-01,
                                   5.34973441e-01, 3.96480384e+06, 2.39392361e-01, 1.90003482e-01,
                                   7.18899146e+00, 1.44145567e-01, 1.69562701e-01])

                for i in range(len(df_mean2)):
                    lr_data2[df_vars2[i]] = (((lr_data2[df_vars2[i]]) - (df_mean2)[i]) / df_std2[i])

                x_test2 = lr_data2.iloc[:, 1:]
                model_pathname2 = os.path.join(model_dir, '%s.model' % 'rf_right')
                rf_right = load_model(pathname=model_pathname2)
                y_pred2 = np.where(rf_right.predict_proba(x_test2)[:, 1] > 0.4553, 1, 0)

                lr_data2['Right_Y'] = y_pred2
                lr_data2['Right_Y'] = ['Normal' if x == 0 else 'Abnormal' for x in lr_data2['Right_Y']]
                # print(lr_data2)
                # lr_data2['Right_prob'] = [x if x > 0.401166 else 1 - x for x in logreg_right.predict_proba(x_test2)[:, 1]]

                #  linear regression on right toe
                lr_data2_reg = pd.DataFrame()
                lr_data2_reg['ID'] = df2['ID']
                df_vars2_reg = ['var_1', 'var_33', 'var_49', 'var_3', 'var_17', 'var_23']
                lr_data2_reg[df_vars2_reg] = df2[df_vars2_reg]

                df_mean2_reg = np.array(
                    [4.74950561e+03, 9.28725830e+03, 1.69165875e-02, -3.08424835e+02, 6.72317947e+03, 3.95782313e-01])

                df_std2_reg = np.array(
                    [5.90609660e+03, 9.43637158e+03, 1.23085160e-01, 8.76354919e+02, 1.19391989e+04, 1.53926722e-01])

                for i in range(len(df_mean2_reg)):
                    lr_data2_reg[df_vars2_reg[i]] = (
                                ((lr_data2_reg[df_vars2_reg[i]]) - (df_mean2_reg)[i]) / df_std2_reg[i])

                x_test2_reg = lr_data2_reg.iloc[:, 1:]
                model_pathname2_reg = os.path.join(model_dir, '%s.model' % 'reg_right')
                reg_right = load_model(pathname=model_pathname2_reg)
                y_pred2_reg = reg_right.predict(x_test2_reg)
                lr_data2_reg['Right_ABI'] = y_pred2_reg


                # print(lr_data2_reg[['var_1', 'var_33', 'var_49', 'var_3', 'var_17', 'var_23']])

                # lr_data = pd.DataFrame()

        # lr_data = reduce(lambda x, y: pd.merge(x, y, on='ID', how='outer'),
        #                  [lr_data1[['ID', 'Left_Y']], lr_data2[['ID', 'Right_Y']]]).reset_index(
        #     drop='True').fillna('Not found')


        try:
            lr_data = reduce(lambda x, y: pd.merge(x, y, on='ID', how='outer'),
                             [lr_data1[['ID', 'Left_Y']], lr_data2[['ID', 'Right_Y']],
                              lr_data1_reg[['ID', 'Left_ABI']], lr_data2_reg[['ID', 'Right_ABI']]]).reset_index(
                drop='True').fillna('Not found')

        except Exception as e:
            tb = sys.exc_info()[-1]
            stk = traceback.extract_tb(tb, 1)
            fname = stk[0][2]
            print('The failing function was', fname)
            Logger.debug(
                'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(e))
            try:
                lr_data = reduce(lambda x, y: pd.merge(x, y, on='ID', how='left'),
                                 [lr_data1[['ID', 'Left_Y']], lr_data1_reg[['ID', 'Left_ABI']]]).reset_index(
                    drop='True').fillna('Not found')
                # lr_data['Right_Y'].loc[0] = ''
                Logger.debug("  '''   Right Toe data not available  ''''  ")

            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                print('The failing function was', fname)
                Logger.debug(
                    'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                        e))
                try:
                    lr_data = reduce(lambda x, y: pd.merge(x, y, on='ID', how='left'),
                                     [lr_data2[['ID', 'Right_Y']], lr_data2_reg[['ID', 'Right_ABI']]]).reset_index(
                        drop='True').fillna('Not found')
                    Logger.debug("  '''   Left Toe data not available  ''''  ")

                except Exception as e:
                    tb = sys.exc_info()[-1]
                    stk = traceback.extract_tb(tb, 1)
                    fname = stk[0][2]
                    print('The failing function was', fname)
                    Logger.debug(
                        'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                            e))
                    Logger.error("  '''''     prediction not done due missing Toe Data.    '''''''   ", exc_info=True)
                    # sys.exit(1)
                # lr_data['Left_Y'].loc[0] = ''

        for i in range(len(lr_data)):
            try:
                if lr_data['Right_Y'][i] == 'Abnormal' and lr_data['Right_ABI'][i] >= 0.90 and lr_data['Left_Y'][
                    i] == 'Abnormal' and lr_data['Left_ABI'][i] >= 0.90:
                    # if lr_data['Left_Y'][i] == 'Abnormal' and lr_data['Left_ABI'][i] >= 0.90:
                    if lr_data['Left_ABI'][i] < lr_data['Right_ABI'][i]:
                        lr_data['Left_ABI'][i] = (lr_data['Left_ABI'][i] / lr_data['Right_ABI'][i]) * 0.90
                        lr_data['Right_ABI'][i] = 0.90
                    elif lr_data['Left_ABI'][i] > lr_data['Right_ABI'][i]:
                        lr_data['Right_ABI'][i] = (lr_data['Right_ABI'][i] / lr_data['Left_ABI'][i]) * 0.90
                        lr_data['Left_ABI'][i] = 0.90

            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                print('The failing function was', fname)
                Logger.debug(
                    'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                        e))
                Logger.error("  '''''     abi correction not done due missing Right1 Toe Data.    '''''''   ",
                             exc_info=True)

            try:
                if lr_data['Right_Y'][i] == 'Normal' and lr_data['Right_ABI'][i] <= 0.9 and lr_data['Left_Y'][
                    i] == 'Normal' and lr_data['Left_ABI'][i] <= 0.9:
                    # if lr_data['Left_Y'][i] == 'Normal' and lr_data['Left_ABI'][i] <= 0.9:
                    if lr_data['Left_ABI'][i] < lr_data['Right_ABI'][i]:
                        if (lr_data['Right_ABI'][i] / lr_data['Left_ABI'][i]) * 0.90 >= 1.30:
                            lr_data['Right_ABI'][i] = 1.30
                        else:
                            lr_data['Right_ABI'][i] = (lr_data['Right_ABI'][i] / lr_data['Left_ABI'][i]) * 0.90
                        lr_data['Left_ABI'][i] = 0.90


                    elif lr_data['Left_ABI'][i] > lr_data['Right_ABI'][i]:
                        if (lr_data['Left_ABI'][i] / lr_data['Right_ABI'][i]) * 0.90 >= 1.30:
                            lr_data['Left_ABI'][i] = 1.30
                        else:
                            lr_data['Left_ABI'][i] = (lr_data['Left_ABI'][i] / lr_data['Right_ABI'][i]) * 0.90
                        lr_data['Right_ABI'][i] = 0.90

            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                print('The failing function was', fname)
                Logger.debug(
                    'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                        e))
                Logger.error("  '''''     abi correction not done due missing Left1 Toe Data.    '''''''   ",
                             exc_info=True)

            try:
                if lr_data['Right_Y'][i] == 'Abnormal' and lr_data['Right_ABI'][i] >= 0.90:
                    lr_data['Right_ABI'][i] = 0.90
                if lr_data['Right_Y'][i] == 'Normal' and lr_data['Right_ABI'][i] <= 0.9:
                    lr_data['Right_ABI'][i] = 0.90
                if lr_data['Right_Y'][i] == 'Normal' and lr_data['Right_ABI'][i] >= 1.30:
                    lr_data['Right_ABI'][i] = 1.30

            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                print('The failing function was', fname)
                Logger.debug(
                    'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                        e))
                Logger.error("  '''''     abi correction not done due missing Right2 Toe Data.    '''''''   ",
                             exc_info=True)

            try:
                if lr_data['Left_Y'][i] == 'Abnormal' and lr_data['Left_ABI'][i] >= 0.90:
                    lr_data['Left_ABI'][i] = 0.90
                if lr_data['Left_Y'][i] == 'Normal' and lr_data['Left_ABI'][i] <= 0.90:
                    lr_data['Left_ABI'][i] = 0.90
                if lr_data['Left_Y'][i] == 'Normal' and lr_data['Left_ABI'][i] >= 1.30:
                    lr_data['Left_ABI'][i] = 1.30

            except Exception as e:
                tb = sys.exc_info()[-1]
                stk = traceback.extract_tb(tb, 1)
                fname = stk[0][2]
                print('The failing function was', fname)
                Logger.debug(
                    'File name - combined.py  ' + '=======  Function name  - ' + fname + "======= exception - " + str(
                        e))
                Logger.error("  '''''     abi correction not done due missing Left2 Toe Data.    '''''''   ",
                             exc_info=True)
        print(lr_data)

        lr_data.to_csv(os.path.join(result_data_dir, '%s.csv' % 'result_left_right'))

        # print(lr_data)

    return lr_data


if __name__ == '__main__':
  result_left()


