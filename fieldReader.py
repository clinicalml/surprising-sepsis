import csv
import datetime
import string
import re


class FieldReader:
    def __init__(self,filename,fields='settings/FIELDS.txt'):
        self.fields = {}
        fieldfile = file(fields)
        self.typer = {}
        for l in fieldfile:
            if '#' == l[0]:
                continue
            elif l.strip() == "":
                continue
            elif '!' == l[0]:
                k,t = l.strip().strip('!').split(':')
                self.typer[k]=t
            else:
                l = l.strip()
                fid = l.split('|')[0]
                if re.match(fid,filename):
                    datatype = l.split('|')[1]
                    fields = l.split('|')[2:]
                    self.fields['comment']=(fid.split('_')[1],)
                    for f in fields:
                        id,vals = f.split(':')
                        vals = vals.split(',')
                        self.fields[id] = vals
 
        print filename, datatype
        self.reader = csv.reader(file(filename))
        self.header = map(string.strip, self.reader.next())
        self.inv_header = dict(zip(self.header, xrange(len(self.header))))

    def __iter__(self):
        return self

    def apply_type(self, datum, fieldname):
        type = self.typer[fieldname]
        if type =='datetime':
            try:
                return datetime.datetime.strptime(datum, "%Y/%m/%d %H:%M:%S")
            except:
                return None
        elif type == 'string':
            return datum
        elif type == 'int':
            return int(datum)

    def next(self):
        fail = True
        while fail:
            l = map(string.strip, self.reader.next())
            retdict = {}
            fail = False
            for k,v in self.fields.items():
                if k == 'comment':
                    retdict[k] = v
                else:
                    try:
                        retdict[k] = tuple([self.apply_type(l[self.inv_header[i]],k) for i in v])
                    except:
                        fail = True

        return retdict

