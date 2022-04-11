
"""List of large size that we've moved to an external file."""

dhall_list = ["Wucox", "RoMa", "Forbes", "CJL", "Whitman"]

majors  = ['African American Studies',
 'Anthropology', 'Architecture',
  'Art and Archaeology', 'Astrophysical Sciences',
   'Chemical and Biological Engineering', 'Chemistry',
    'Civil and Environmental Engineering', 'Classics',
     'Comparative Literature', 'Computer Science - A.B.',
      'Computer Science - B.S.E.', 'East Asian Studies',
       'Ecology and Evolutionary Biology', 'Economics',
        'Electrical and Computer Engineering', 'English',
         'French and Italian', 'Geosciences', 'German',
          'History', 'Mathematics',
           'Mechanical and Aerospace Engineering',
            'Molecular Biology', 'Music', 'Near Eastern Studies',
             'Neuroscience',
              'Operations Research and Financial Engineering',
               'Philosophy', 'Physics', 'Politics',
                'Psychology', 'Religion',
                 'School of Public and International Affairs',
                  'Slavic Languages and Literatures',
                   'Sociology', 'Spanish and Portuguese']
dc = [
'AAS','ANT','ARC','ART','AST','CBE',
'CHM','CEE','CLA','COM','COS AB',
'COS BSE','EAS','EEB','ECO','ECE',
'ENG','FRE/ITA','GEO', 'GER', 'HIS','MAT','MAE',
'MOL','MUS','NES','NEU','ORFE',
'PHI','PHY','POL','PSY','REL',
'SPIA','SLA','SOC','SPA/POR']
dept_code = dict(zip(majors, dc))