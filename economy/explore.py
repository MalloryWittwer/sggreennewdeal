import pandas as pd
import matplotlib.pyplot as plt
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

data_tables = {
    'services_exports':{'filename':os.path.join(ROOT_DIR, 'SGP_services.csv')},
    'services_imports': {'filename': os.path.join(ROOT_DIR, 'SGP_services_imports.csv')},
    'employment': {'filename': os.path.join(ROOT_DIR, 'employment_by_industry.csv')},
    'services_expense': {'filename': os.path.join(ROOT_DIR, 'services_expenditures.csv')},
    'services_emission_factors': {'filename': os.path.join(ROOT_DIR, 'services_emission_factors.csv')},
}

CAT_FIELDS = ['Year','Region','Country']

def read_tables():
    for f in data_tables:
        data_tables[f]['table'] = pd.read_csv(data_tables[f]['filename'])

#employment
#------------------------------------------------------------------------

EMP_CAT_FIELDS = ['Year','Occupation group']

def emp_analysis():
    read_tables()
    emp_cleanup()
    tbl = data_tables['employment']['table'].copy()

def emp_cleanup():
    tbl = data_tables['employment']['table'].copy()
    tbl.fillna(0,inplace=True)
    occp_groups = list(tbl['Occupation group'].unique())
    industries = [x for x in tbl.columns if not x in EMP_CAT_FIELDS]

    data_tables['employment']['Occupation groups'] = occp_groups
    data_tables['employment']['Industries'] = industries
    data_tables['employment']['table'] = tbl

def emp_by_occp_group(industries=None):
    tbl = data_tables['employment']['table'].copy()
    if industries is None:
        industries = data_tables['employment']['Industries']
    tbl['all industries'] = tbl[industries].sum(1)
    pvt = pd.pivot_table(tbl,index=['Year'],columns=['Occupation group'],
                         values=['all industries'],aggfunc=sum)
    return pvt['all industries']

def emp_by_industry(occp_groups=None):
    tbl = data_tables['employment']['table'].copy()
    if occp_groups is None:
        occp_groups = data_tables['employment']['Occupation groups']
    industries = data_tables['employment']['Industries']
    tbl.set_index('Year', inplace=True)
    tb_set = [tbl[tbl['Occupation group'] == x][industries] for x in occp_groups]
    tb_all = sum(tb_set)
    return tb_all

def plot_tbl(tbl,ax):
    graph_scale = 0.7
    fontsize = 6
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * graph_scale, box.height])
    tbl.plot(kind='bar', stacked=True, ax=ax)
    plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5),prop={'size':6})

#services
#------------------------------------------------------------------------

def services_analysis():
    read_tables()
    srv_cleanup()

def srv_cleanup():
    #create service table - add others
    for t in ['services_exports','services_imports']:
        tbl = data_tables[t]['table']
        tbl = add_others(tbl)
        data_tables[t]['table'] = tbl

def srv_by_country(tbl_flag='services_exports'):
    tbl = data_tables[tbl_flag]['table']
    tbl['srv totals'] = tbl[[x for x in tbl.columns if not x in CAT_FIELDS]].sum(1)
    pvt = pd.pivot_table(tbl, index=['Year'],
                         columns=['Country'],values='srv totals', aggfunc=sum)
    return pvt

def srv_by_service(tbl_flag='services_exports'):
    tbl = data_tables[tbl_flag]['table']
    pvt = pd.pivot_table(tbl, index=['Year'],
                         values=[x for x in tbl.columns if not x in CAT_FIELDS], aggfunc=sum)
    return pvt

def get_region_slice(region,tbl):
    slice = tbl[tbl.Region == region]
    return slice

def add_others(tbl):
    regions = list(tbl.Region.unique())
    for r in regions:
        tbl = add_region_others(tbl, r)
    tbl.fillna(0,inplace=True)
    return tbl

def add_region_others(tbl,r):
    slc = get_region_slice(r, tbl).copy()
    slc_total = slc[slc.Country == 'Total']
    if len(slc_total)>0:
        slc_total = slc_total[[x for x in tbl.columns if not x in ['Country','Region']]].fillna(0)
        slc_total.set_index('Year',inplace=True)
        slc_extotal = pd.pivot_table(slc[slc.Country != 'Total'].fillna(0), index=['Year'],
                                   values=[x for x in tbl.columns if not x in CAT_FIELDS], aggfunc=sum)
        ex = slc_total-slc_extotal
        ex['Region'] = r
        ex['Country'] = r + ' others'
        ex.reset_index(inplace=True)
        tbl.drop(slc[slc.Country == 'Total'].index,inplace=True)
        tbl=tbl.append(ex)
    return tbl

#services emissions intensity
#------------------------------------------------------------------------

SRV_EXP_CAT_FIELDS = ['Year','Services sector']

def serv_exp_cleanup():
    # 'services_expense'
    # 'services_emission_factors'

    tbl_srv = data_tables['services_expense']['table'].copy()
    tbl_ef = data_tables['services_emission_factors']['table'].copy()
    tbl_srv.fillna(0,inplace=True)
    tbl_ef.fillna(0,inplace=True)

#    occp_groups = list(tbl['Occupation group'].unique())
#    industries = [x for x in tbl.columns if not x in EMP_CAT_FIELDS]

#    data_tables['employment']['Occupation groups'] = occp_groups
#    data_tables['employment']['Industries'] = industries

    data_tables['services_expense']['table'] = tbl_srv
    data_tables['services_emission_factors']['table'] = tbl_ef

def srv_emissions_intensity_tbl():
    tbl_srv = data_tables['services_expense']['table'].copy()
    tbl_ef = data_tables['services_emission_factors']['table'].copy()

    mtbl = pd.melt(tbl_srv, id_vars=SRV_EXP_CAT_FIELDS,
                     value_vars=[x for x in tbl_srv.columns if not x in SRV_EXP_CAT_FIELDS],
                     var_name='Expense type')
    btbl = pd.merge(mtbl, tbl_ef, on='Expense type')
    btbl['Emissions tCO2'] = btbl['value'] * btbl['Emissions factor kgCO2/SGD'] / 1000
    return btbl

def srv_expense_by_group(units='value',year=2017,showall=False):
    btbl = srv_emissions_intensity_tbl()
    ptype = pd.pivot_table(btbl, index=['Year', 'Services sector'],
                             columns=['Group'], values=[units], aggfunc=sum)[units]
    if not showall:
        ptype = ptype[[x for x in ptype.columns if not x == 'Excluded']].copy()
    return ptype.loc[year]

