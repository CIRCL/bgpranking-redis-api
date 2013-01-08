# -*- coding: utf-8 -*-
"""
    View class of the website
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The website respects the MVC design pattern and this class is the view.

"""

import os
import cherrypy
from Cheetah.Template import Template
import ConfigParser
import cgi
from csv import DictReader
import urllib2
import json

import master_controler

def merge_csvs(asns):
    asns = json.loads(asns)
    if asns[0] == 0:
        return json.dumps('')
    temp_dict = {}
    no_entries = []
    for asn in asns:
        try:
            f = urllib2.urlopen('http://127.0.0.1:8080/csv/' + asn)
            for line in DictReader(f):
                date = line['day']
                rank = line['rank']
                if temp_dict.get(date) is None:
                    temp_dict[date] = {}
                temp_dict[date][asn] = rank
        except:
            no_entries += asn
    to_return = 'date,' + ','.join(asns) + '\n'
    for date, entries in temp_dict.iteritems():
        to_return += date
        for asn in asns:
            rank = entries.get(asn)
            if rank is None:
                rank = 0
            to_return += ',' + str(rank)
        to_return += '\n'
    return json.dumps(to_return)


class Master(object):

    def __init__(self):
        self.dir_templates = 'templates'

    def __none_if_empty(self, to_check = None):
        """
            Ensure the empty paramaters are None before doing anything
        """
        if to_check is None or len(to_check) == 0:
            return None
        return cgi.escape(to_check, True)

    def __init_template(self, template_name, source = None, date = None):
        """
            Initialize the basic components of the template
        """
        template = Template(file = os.path.join(self.dir_templates,
            template_name + '.tmpl'))
        source = self.__none_if_empty(source)
        date = self.__none_if_empty(date)
        template.css_file = 'http://www.circl.lu/css/styles.css'
        template.logo = 'http://www.circl.lu/pics/logo.png'
        template.banner = 'http://www.circl.lu/pics/topbanner.jpg'
        template.sources = master_controler.get_sources(date)
        template.dates = master_controler.get_dates()
        template.source = source
        template.date = date
        return template

    @cherrypy.expose
    def default(self):
        """
            Load the index
        """
        return str(self.index())

    @cherrypy.expose
    def index(self, source = None, asn = None, date = None):
        """
            Generate the view of the global ranking
        """
        source = self.__none_if_empty(source)
        asn = self.__none_if_empty(asn)
        date = self.__none_if_empty(date)
        histo = master_controler.prepare_index(source, date)
        template = self.__init_template('index_asn', source, date)
        template.histories = histo
        return str(template)

    @cherrypy.expose
    def asn_details(self, source = None, asn = None, ip_details = None, date = None):
        """
            Generate the view of an ASN
        """
        asn = self.__none_if_empty(asn)
        source = self.__none_if_empty(source)
        date = self.__none_if_empty(date)
        if asn is None:
            return self.index(source, asn, date)
        ip_details = self.__none_if_empty(ip_details)
        template = self.__init_template('asn_details', source, date)
        asn = asn.lstrip('AS')
        if asn.isdigit():
            template.asn = asn
            as_infos = master_controler.get_as_infos(asn, source, date)
            if as_infos is not None and len(as_infos) > 0:
                template.asn_descs = as_infos
                template.current_sources = master_controler.get_last_month_sources()
                if len(template.current_sources.keys()) > 0:
                    template.sources = template.current_sources.keys()
                if ip_details is not None:
                    template.ip_details = ip_details
                    template.ip_descs = master_controler.get_ip_info(asn,
                            ip_details, source, date)
        else:
            template.error = "Invalid query: " +  asn
        return str(template)

    @cherrypy.expose
    def comparator(self, asns = None):
        """
            Generate the view comparing a set of ASNs
        """
        asns = self.__none_if_empty(asns)
        template = self.__init_template('comparator')
        template.asns = asns
        if asns is not None:
            template.asns_json = json.dumps(asns.split())
        else:
            template.asns_json = json.dumps([0])
        return str(template)

    @cherrypy.expose
    def trend(self):
        """
            Print the trend World vs Luxembourg
        """
        return str(self.__init_template('trend'))

    @cherrypy.expose
    def map(self):
        """
            Print the worldmap
        """
        return str(self.__init_template('map'))

def error_page_404(status, message, traceback, version):
    """
        Display an error if the page does not exists
    """
    return "Error %s - This page does not exist." % status

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)

    website = Master()

    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.quickstart(website, config = config.get('web','config_file'))
