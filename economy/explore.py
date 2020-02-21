import pandas as pd
data_tables = {
    'services_exports':{'filename':'SGP_services.csv'},
}

CAT_FIELDS = ['Year','Region','Country']

def read_tables():
    for f in data_tables:
        data_tables[f]['table'] = pd.read_csv(data_tables[f]['filename'])


def service_export_analysis():
    read_tables()
    srvexp_cleanup()

def srvexp_cleanup():
    #create service table - add others
    tbl = data_tables['services_exports']['table']
    tbl = add_others(tbl)
    data_tables['services_exports']['table'] = tbl

def srvexp_by_srv_type():
    tbl = data_tables['services_exports']['table']
    pvt = pd.pivot_table(tbl, index=['Year'],
                         values=[x for x in tbl.columns if not x in e.CAT_FIELDS], aggfunc=sum)


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