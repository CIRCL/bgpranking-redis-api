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
import csv
import StringIO
from csv import DictReader
import urllib2
import json
from cherrypy import _cperror

import master_controler
from pubsublogger import publisher

def merge_csvs(asns):
    url = 'http://{host}:{port}/csv/'.format(
            host = cherrypy.config.get('server.socket_host'),
            port = cherrypy.config.get('server.socket_port'))
    asns = json.loads(asns)
    if asns[0] == 0:
        return json.dumps('')
    temp_dict = {}
    no_entries = []
    for asn in asns:
        try:
            f = urllib2.urlopen(url + asn)
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
        publisher.channel = 'Website'

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

    def __csv2string(self, data):
        si = StringIO.StringIO();
        cw = csv.writer(si);
        cw.writerow(data);
        return si.getvalue().strip('\r\n');

    def __query_logging(self, ip, user_agent, webpage, date=None, source=None,
            asn=None, asn_details=None, compared_asns=None, ip_lookup=None):
        publisher.info(self.__csv2string([ip, user_agent, webpage, date,
                source, asn, asn_details, compared_asns, ip_lookup]))

    @cherrypy.expose
    def default(self):
        """
            Load the index
        """
        return str(self.index())

    @cherrypy.expose
    def index(self, source = None, date = None):
        """
            Generate the view of the global ranking
        """
        source = self.__none_if_empty(source)
        date = self.__none_if_empty(date)
        self.__query_logging(cherrypy.request.remote.ip,
            cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
            webpage='index', date=date, source=source)
        histo, list_size = master_controler.prepare_index(source, date)
        template = self.__init_template('index_asn', source, date)
        template.list_size = list_size
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
            return self.index(source, date)
        self.__query_logging(cherrypy.request.remote.ip,
            cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
            webpage='asn_details', date=date, source=source, asn=asn,
            asn_details = ip_details)
        ip_details = self.__none_if_empty(ip_details)
        template = self.__init_template('asn_details', source, date)
        asn = asn.lstrip('AS')
        if asn.isdigit():
            template.asn = asn
            asn_description, position, as_infos = master_controler.get_as_infos(asn,
                    date, source)
            if as_infos is not None and len(as_infos) > 0:
                template.asn_description = asn_description
                template.asn_descs = as_infos
                template.current_sources = master_controler.get_last_seen_sources(asn)
                template.desc_history = master_controler.get_asn_descriptions(asn)
                template.position = position[0]
                template.size = position[1]
                if len(template.current_sources.keys()) > 0:
                    template.sources = template.current_sources.keys()
                if ip_details is not None:
                    template.ip_details = ip_details
                    template.ip_descs = master_controler.get_ip_info(asn,
                            ip_details, date, source)
        else:
            template.error = "Invalid query: " +  asn
        return str(template)

    @cherrypy.expose
    def comparator(self, asns = None):
        """
            Generate the view comparing a set of ASNs
        """
        asns = self.__none_if_empty(asns)
        self.__query_logging(cherrypy.request.remote.ip,
            cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
            webpage='comparator', compared_asns=asns)
        template = self.__init_template('comparator')
        template.asns = asns
        if asns is not None:
            asns_list, details_list = master_controler.get_comparator_metatada(asns)
            template.asns_json = json.dumps(asns_list)
            template.asns_details = details_list
        else:
            template.asns_json = json.dumps([0])
            template.asns_details = None
        return str(template)

    @cherrypy.expose
    def trend(self):
        """
            Print the trend World vs Luxembourg
        """
        return self.trend_benelux()
        #self.__query_logging(cherrypy.request.remote.ip,
        #    cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
        #    webpage='trend')
        #return str(self.__init_template('trend'))

    @cherrypy.expose
    def trend_benelux(self):
        """
            Print the trend of the benelux countries
        """
        self.__query_logging(cherrypy.request.remote.ip,
            cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
            webpage='trend_benelux')
        return str(self.__init_template('trend_benelux'))

    @cherrypy.expose
    def map(self):
        """
            Print the worldmap
        """
        self.__query_logging(cherrypy.request.remote.ip,
            cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
            webpage='map')
        return str(self.__init_template('map'))

    @cherrypy.expose
    def ip_lookup(self, ip = None):
        ip = self.__none_if_empty(ip)
        self.__query_logging(cherrypy.request.remote.ip,
                cherrypy.request.headers.get('User-Agent', 'Empty User-Agent'),
                webpage='ip_lookup', ip_lookup=ip)
        template = self.__init_template('ip_lookup')
        template.ip = ip
        history = master_controler.get_ip_lookup(ip)
        template.history = history
        return str(template)

def error_page_404(status, message, traceback, version):
    """
        Display an error if the page does not exists
    """
    return "Error %s - This page does not exist." % status

def handle_error():
    cherrypy.response.status = 500
    cherrypy.response.body = ["<html><body>Sorry, an error occured</body></html>"]
    publisher.error('Request: '+ str(cherrypy.request.params) + '\n' +_cperror.format_exc())

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)

    website = Master()

    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.config.update({'request.error_response': handle_error})
    cherrypy.quickstart(website, config = config.get('web','config_file'))
