"""
Script that takes specified CSV-formatted output file, which is generated
by taxcalc.sas, and translates that information into a file that has an
Internet-TAXSIM output format.
"""
# CODING-STYLE CHECKS:
# pep8 --ignore=E402 sas2out.py
# pylint --disable=locally-disabled sas2out.py
# (when importing numpy, add "--extension-pkg-whitelist=numpy" pylint option)


import os
import sys
import argparse
import pandas as pd
CUR_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(CUR_PATH, '..', '..'))
from taxcalc import SimpleTaxIO  # pylint: disable=import-error


EXPECTED_INPUT_VARS = set([
    'e00650', 'e02500', 'RECID', '_cmbtp', '_amtspa', '_edical',
    'c82880', 'c82885', 'c82890', 'c82900', 'c82905', 'c82910',
    'c82915', 'c82920', 'c82925', 'c82930', 'c82935', 'c82937',
    'c82940', 'c00100', 'c01000', 'c02500', 'c02650', 'c02700',
    'c02900', 'c04100', 'c04200', 'c04470', 'c04500', 'c04600',
    'c04800', 'c05100', 'c05200', 'c05700', 'c05750', 'c05800',
    'c07100', 'c07150', 'c07180', 'c07220', 'c07230', 'c07970',
    'c08795', 'c08800', 'c09200', 'c09600', 'c10300', 'c10950',
    'c10960', 'c11055', 'c11070', 'c15100', 'c15200', 'c17000',
    'c17750', 'c18300', 'c19200', 'c19700', 'c20400', 'c20500',
    'c20750', 'c20800', 'c21040', 'c21060', 'c23650', 'c24505',
    'c24510', 'c24516', 'c24517', 'c24520', 'c24530', 'c24534',
    'c24540', 'c24550', 'c24560', 'c24570', 'c24580', 'c24597',
    'c24598', 'c24610', 'c24615', 'c32800', 'c32840', 'c32880',
    'c32890', 'c33000', 'c33200', 'c33400', 'c33465', 'c33470',
    'c33475', 'c33480', 'c37703', 'c59430', 'c59450', 'c59460',
    'c59485', 'c59490', 'c59560', 'c59660', 'c59680', 'c59700',
    'c59720', 'c60000', 'c60130', 'c60200', 'c60220', 'c60240',
    'c60260', 'c62100', 'c62600', 'c62700', 'c62720', 'c62730',
    'c62740', 'c62745', 'c62747', 'c62755', 'c62770', 'c62780',
    'c62800', 'c62900', 'c63000', 'c63100', 'c64450', 'c87482',
    'c87483', 'c87487', 'c87488', 'c87492', 'c87493', 'c87497',
    'c87498', 'c87521', 'c87530', 'c87540', 'c87550', 'c87560',
    'c87570', 'c87580', 'c87590', 'c87600', 'c87610', 'c87620',
    'c87654', 'c87656', 'c87658', 'c87660', 'c87662', 'c87664',
    'c87666', 'c87668', 'c87681', 'c03260', 'c09400', '_addamt',
    '_addtax', '_agep', '_ages', '_agierr', '_alminc', '_amt',
    '_amtfei', '_amtstd', '_cglong', '_ctc1', '_ctc2', '_ctcagi',
    '_ctctax', '_dclim', '_dwks12', '_dwks16', '_dwks17',
    '_dwks21', '_dwks25', '_dwks26', '_dwks28', '_dwks31',
    '_dwks5', '_dwks9', '_dy', '_earned', '_exocrd', '_feided',
    '_feitax', '_fica', '_ieic', '_limitratio', '_line17',
    '_line19', '_line22', '_line30', '_line31', '_line32',
    '_line33', '_line34', '_line35', '_line36', '_modagi',
    '_nbertax', '_nctcr', '_ngamty', '_noncg', '_nonlim',
    '_num', '_numxtr', '_othadd', '_othded', '_othtax',
    '_parents', '_posagi', '_precrd', '_preeitc', '_prexmp',
    '_regcrd', '_s1291', '_sey', '_secwage', '_statax',
    '_stndrd', '_tamt2', '_taxbc', '_taxcg', '_taxinc',
    '_tratio', '_txpyrs', '_val_rtbase', '_val_rtless',
    '_val_ymax', '_xyztax', '_ymod', '_ymod1', '_ymod2',
    '_ymod3', '_amt1513', '_soitax'])


def main(infilename, outfilename):
    """
    Contains high-level logic of the script.
    """
    # read INPUT file into a Pandas DataFrame
    inputdf = pd.read_csv(infilename)
    actual_input_vars = set(inputdf.columns.values)
    assert actual_input_vars == EXPECTED_INPUT_VARS

    # translate INPUT variables into OUTPUT lines
    olines = ''
    for idx in range(0, inputdf.shape[0]):
        rec = inputdf.xs(idx)
        odict = extract_output(rec)
        olines += SimpleTaxIO.construct_output_line(odict)

    # write OUTPUT lines to OUTPUT file
    with open(outfilename, 'w') as outfile:
        outfile.write(olines)

    # return no-error exit code
    return 0
# end of main function code


def extract_output(rec):
    """
    Extracts tax output from tax filing unit rec.

    Parameters
    ----------
    rec: Pandas Series indexed by variable names in EXPECTED_INPUT_VARS set.

    Returns
    -------
    ovar: dictionary of output variables indexed from 1 to SimpleTaxIO.OVAR_NUM

    Notes
    -----
    The value of each output variable is stored in the ovar dictionary,
    which is indexed as Internet-TAXSIM output variables are (where the
    index begins with one).
    """
    ovar = {}
    ovar[1] = int(rec['RECID'])  # id for tax filing unit
    ovar[2] = 2013  # year for which taxes are calculated
    ovar[3] = 0  # state code is always zero
    ovar[4] = rec['_nbertax']  # federal income tax liability
    ovar[5] = 0.0  # no state income tax calculation
    ovar[6] = 0.0  # NOT IN TAXCALC.SAS : FICA taxes (ee+er) for OASDI+HI
    ovar[7] = 0.0  # marginal federal income tax rate as percent
    ovar[8] = 0.0  # no state income tax calculation
    ovar[9] = 0.0  # marginal FICA tax rate as percent
    ovar[10] = rec['c00100']  # federal AGI
    ovar[11] = 0.0  # UI benefits in AGI
    ovar[12] = rec['c02500']  # OASDI benefits in AGI
    ovar[13] = 0.0  # always set zero-bracket amount to zero
    pre_phase_out_pe = rec['_prexmp']
    post_phase_out_pe = rec['c04600']
    phased_out_pe = pre_phase_out_pe - post_phase_out_pe
    ovar[14] = post_phase_out_pe  # post-phase-out personal exemption
    ovar[15] = phased_out_pe  # personal exemption that is phased out
    # ovar[16] can be positive for non-itemizer:
    ovar[16] = rec['c21040']  # itemized deduction that is phased out
    # ovar[17] is zero for non-itemizer:
    ovar[17] = rec['c04470']  # post-phase-out itemized deduction
    ovar[18] = rec['c04800']  # federal regular taxable income
    ovar[19] = rec['c05200']  # regular tax on taxable income
    ovar[20] = 0.0  # always set exemption surtax to zero
    ovar[21] = 0.0  # always set general tax credit to zero
    ovar[22] = rec['c07220']  # child tax credit (adjusted)
    ovar[23] = rec['c11070']  # extra child tax credit (refunded)
    ovar[24] = rec['c07180']  # child care credit
    ovar[25] = 0.0  # NOT IN TAXCALC.SAS : crecs._eitc[idx]  # federal EITC
    ovar[26] = rec['c62100']  # federal AMT taxable income ? _everybody ?
    amt_liability = rec['c09600']  # federal AMT liability
    ovar[27] = amt_liability
    # ovar[28] is federal income tax before credits; the variable
    # rec['c05800'] is this concept but includes AMT liability while
    # Internet-TAXSIM ovar[28] explicitly excludes AMT liability, so
    # we have the following:
    ovar[28] = rec['c05800'] - amt_liability
    return ovar
# end of extract_output function code


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        prog='python sas2out.py',
        description=('Reads CSV-formatted INPUT file containing '
                     'taxcalc.sas output results and writes an '
                     'OUTPUT file with Internet-TAXSIM output format.'))
    PARSER.add_argument('INPUT',
                        help=('INPUT is name of required file that contains '
                              'CSV-formatted taxcalc.sas output results.'))
    PARSER.add_argument('OUTPUT',
                        help=('OUTPUT is name of required file that contains '
                              'output results in Internet-TAXSIM format.'))
    ARGS = PARSER.parse_args()
    sys.exit(main(ARGS.INPUT, ARGS.OUTPUT))
