from economy import explore as e

e.read_tables()

#services exports
e.srv_cleanup()

exp = e.data_tables['services_exports']['table']
imp = e.data_tables['services_imports']['table']

exp_by_country = e.srv_by_country('services_exports')
imp_by_country = e.srv_by_country('services_imports')

exp_by_service = e.srv_by_service('services_exports')
imp_by_service = e.srv_by_service('services_imports')

#employment
e.emp_cleanup()

industries = e.data_tables['employment']['Industries']
occp_groups = e.data_tables['employment']['Occupation groups']

#all occp groups
tbl_emp_by_ind = e.emp_by_industry()

#all industries
tbl_emp_by_occp_grp = e.emp_by_occp_group()

sunset = ['Manufacturing : Total','Services : Wholesale & Retail Trade ',
          'Services : Transportation & Storage ']

prof_srv = ['Services : Information & Communications ','Services : Fincial & Insurance',
          'Services : Business misc','Services : Real Estate','Services : Professional',
            'Services : Administrative & Support',' Other Industries']

social_community = ['Services : Public Administration & Education','Services : Health & Social',
          'Services : Arts, Entertainment & Recreation ','Services : Other Community, Social & Personal']

#sunset industries
tbl_emp_sunset = e.emp_by_occp_group(sunset)

#... for prof services, social/community


#to plot stacked charts :
"""   
    f = e.plt.figure()
    ax = e.plt.subplot(111)
    e.plot_tbl(tbl,ax)
"""
