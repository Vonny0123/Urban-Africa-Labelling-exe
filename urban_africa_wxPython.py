# -*- coding: utf-8 -*-
"""
Created on Thu Aug 27 10:12:28 2020

@author: ewand
"""
import wx
import numpy as np
import pandas as pd
import geopandas as gpd
import dask.dataframe as dd
import jellyfish
import xlrd
import os
import pyproj._datadir, pyproj.datadir
from dask.callbacks import Callback
from multiprocessing import freeze_support

class UAFrame(wx.Frame):
    """
    A Frame that contains the UrbanAfrica labelling tool 
    """

    def __init__(self):
        self.data = pd.DataFrame()
        self.col_names = ['country', 'something else']
        self.countries = ['list of countries']
        # ensure the parent's __init__ is called
        super().__init__(parent=None, title='UrbanAfrica', size=(1000, 750))

        # create a panel in the frame
        self.pnl = wx.ScrolledWindow(self)
        self.pnl.SetScrollbars(20, 20, 600, 400)

        # put some text with a larger bold font on it
        st_title = wx.StaticText(self.pnl, label="Urban Africa Labelling")
        font = st_title.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st_title.SetFont(font)
                
        st_description = wx.StaticText(self.pnl, label=f"This application will label entries in a dataset as urban or rural based on latitude and longitude using the Africapolis dataset.")
        
        st_step1 = wx.StaticText(self.pnl, label="Step 1 - Select your CSV file containing longitude/latitude pairs:\n")

        self.picker_df = wx.FilePickerCtrl(self.pnl, message='Select your CSV file...', size=wx.Size(350,25))
        
        st_step2 = wx.StaticText(self.pnl, label="Step 2 - Select the SHP file containing the Africapolis dataset, or leave blank if you do not have this file downloaded:\n")

        self.picker_africapolis = wx.FilePickerCtrl(self.pnl, message='Select your CSV file...', size=wx.Size(350,25))
        
        st_step3 = wx.StaticText(self.pnl, label="Step 3 - When you are happy with the above selections, click to load the selected data.\n")

        self.button_upload = wx.Button(self.pnl, label="Load Data", size=wx.Size(200,25))

        # and create a sizer to manage the layout of child widgets
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.sizer.Add(st_title, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.sizer.Add(st_description, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.sizer.Add(st_step1, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.sizer.Add(self.picker_df, wx.SizerFlags().Border(wx.LEFT, 70))
        self.sizer.Add(st_step2, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.sizer.Add(self.picker_africapolis, wx.SizerFlags().Border(wx.LEFT, 70))
        self.sizer.Add(st_step3, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.sizer.Add(self.button_upload, wx.SizerFlags().Border(wx.LEFT, 70))
        
        self.pnl.SetSizer(self.sizer)
        
        # Bind events to methods
        self.Bind(wx.EVT_BUTTON, self.upload_data, id=self.button_upload.GetId())
        
        #EVT_RESULT(self,self.OnProgReport)

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("Welcome to the Urban Africa Labelling App!")
                    
    def upload_data(self, event):
        self.button_upload.Disable()
        self.button_upload.SetBackgroundColour('#afeeee')
        self.button_upload.SetLabel('Loading Files...')
                
        try:
            self.data = pd.read_csv(self.picker_df.GetPath())
            if self.picker_africapolis.GetPath() == '':
                africapolis_url = 'http://www.africapolis.org/download/Africapolis_2015_shp.zip'
                self.africapolis = gpd.read_file(africapolis_url)
            else:
                self.africapolis = gpd.read_file(self.picker_africapolis.GetPath())
            self.button_upload.SetBackgroundColour('#b4eeb4')
            self.button_upload.SetLabel('Load Successful')
            
            self.col_names = self.data.columns
            
            st_step4 = wx.StaticText(self.pnl, label="Step 4 - If your dataset contains a 'Country' column, we can use this information to use only the relevant Africapolis data and speed up computation. \n              To implement this, check this box and select the column header containing the countries in your data. You may have to provide additional\n              information if the country names in your data do not match with those in the Africapolis dataset.\n")
            self.cb_filter_countries = wx.CheckBox(self.pnl, label="Check to filter countries.")
            st_step5 = wx.StaticText(self.pnl, label="Step 5 - Select the column names containing the longitude and latitude data respectively. \n")
            self.dd_long = wx.ComboBox(self.pnl, choices=self.col_names, size=wx.Size(200,25), value='Select Longitude Column')
            self.dd_lat = wx.ComboBox(self.pnl, choices=self.col_names, size=wx.Size(200,25), value='Select Latitude Column')
            st_step6 =  wx.StaticText(self.pnl, label="Step 6 - When you are happy with the input you have provided, begin the data processing.\n")
            self.button_begin = wx.Button(self.pnl, label="Begin Processing", size=wx.Size(200,50))
                                          
            self.sizer.Add(st_step4, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
            self.sizer.Add(self.cb_filter_countries, wx.SizerFlags().Border(wx.LEFT, 70))
            self.sizer.Add(st_step5, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
            self.sizer.Add(self.dd_long, wx.SizerFlags().Border(wx.LEFT, 70))
            self.sizer.Add(self.dd_lat, wx.SizerFlags().Border(wx.LEFT, 70))
            self.sizer.Add(st_step6, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
            self.sizer.Add(self.button_begin, wx.SizerFlags().Border(wx.LEFT, 70))
            
            self.Bind(wx.EVT_CHECKBOX, self.OnFiltClick, id=self.cb_filter_countries.GetId())
            self.Bind(wx.EVT_BUTTON, self.OnBeginClick, id=self.button_begin.GetId())
            
            self.sizer.Layout()
        except Exception as e:
            self.button_upload.SetBackgroundColour('#f6546a')
            data_success = os.path.isfile(self.picker_df.GetPath())
            africapolis_success = os.path.isfile(self.picker_africapolis.GetPath())
            self.button_upload.SetLabel(f'Error: Check the selected files, {data_success}, {africapolis_success}')
            self.SetStatusText(str(e))
            print(e)
            
    def process_africapolis(self):
        polys = self.africapolis.geometry #This is a series of polygons
        self.containment_checker = polys.geometry.buffer(0).contains
        
    def multi_process_containment_tests(self):
        points = gpd.GeoDataFrame(self.data.loc[:,[self.long_name,self.lat_name]], geometry=gpd.points_from_xy(self.data.loc[:,self.long_name], self.data.loc[:,self.lat_name])) #create a series of point objects representing location of events
        containment_checker = self.containment_checker
        cb = Callback(posttask=self.ProgCallback)
        with cb:# ProgressBar(): 
            r = dd.from_pandas(points.geometry, npartitions=100).map_partitions(lambda dframe: pd.Series(np.any(dframe.apply(containment_checker), axis=1)), meta=pd.Series(dtype=bool)).compute(scheduler='processes')  
        return r
    
    def validate_countries(self, event):
        
        self.button_validate_countries.SetBackgroundColour('#afeeee')
        self.button_validate_countries.SetLabel('Processing your data')
        self.countries = [country.upper() for country in np.unique(self.data[self.col_names[self.dd_country_selector.GetCurrentSelection()]])]
        
        countries_url = 'http://www.africapolis.org/download/Africapolis_country.xlsx'
        countries_data = pd.read_excel(countries_url, skiprows=15)
        self.iso_lookup = dict(zip([string.upper() for string in countries_data.Country], countries_data.ISO))
        
        self.valid_countries = list()
        self.country_dropdowns = list()

        for country in self.countries:
            if country not in self.iso_lookup.keys():
                sim_metrics = [jellyfish.levenshtein_distance(country, valid_country) for valid_country in self.iso_lookup.keys()]
                ordered_valid_countries = [x for _, x in sorted(zip(sim_metrics,self.iso_lookup.keys()), key=lambda pair: pair[0])]
                self.country_dropdowns.append(wx.ComboBox(self.pnl, choices=['My country is not on the list!'] + ordered_valid_countries, size=wx.Size(750,25), value=f'{country} does not appear in Africapolis dataset, select the corresponding valid country name.'))
            else:
                self.valid_countries.append(country)
                
        for i, dropdown in enumerate(self.country_dropdowns):
            self.sizer.Insert(12+i, dropdown, wx.SizerFlags().Border(wx.LEFT, 70))
            self.sizer.Layout()
        self.pnl.SetScrollbars(20, 20, 600, 400, yPos=400)
        self.button_filter_countries = wx.Button(self.pnl, label='Proceed with replacements', size=wx.Size(200,25))
        self.sizer.Insert(12+len(self.country_dropdowns), self.button_filter_countries, wx.SizerFlags().Border(wx.LEFT, 70))
        self.Bind(wx.EVT_BUTTON, self.filter_countries, id=self.button_filter_countries.GetId())   
        #self.sizer.Remove(12)
        self.button_validate_countries.Hide()
        self.sizer.Layout()
        self.Layout()
        
    def filter_countries(self, event):
        warning_given = False
        for dropdown in self.country_dropdowns:
            response = dropdown.GetStringSelection()
            if response not in ['My country is not on the list!', '']:
                self.valid_countries.append(response)
            elif not warning_given:
                 wx.MessageBox("If you are unable to find a country in the dropdown list, it may be missing from the Africapolis dataset. For example, Madagascar is not included. If you proceed, therefore, any data point in such a country will be labelled as urban.")
                 warning_given = True
            
        iso_list = [self.iso_lookup[country] for country in self.valid_countries]
        bools = [iso in iso_list for iso in self.africapolis.ISO]
        self.africapolis = self.africapolis[bools]
        self.button_filter_countries.Disable()
        self.button_filter_countries.SetBackgroundColour('#b4eeb4')
        self.button_filter_countries.SetLabel('Filtering Successful')
        
            
    def OnBeginClick(self, event):
        wx.BeginBusyCursor()
        self.button_begin.Disable()
        self.button_begin.SetBackgroundColour('#afeeee')
        self.button_begin.SetLabel('Processing Your Data...')
        self.long_name=self.dd_long.GetStringSelection()
        self.lat_name=self.dd_lat.GetStringSelection()
        self.process_africapolis()

        self.prog = 0
        
        self.progress = wx.StaticText(self.pnl, label='\n|' + '#'*(self.prog) + '-'*(100-self.prog) + '| ' + str(self.prog) + '%\n')
        self.sizer.Add(self.progress, wx.SizerFlags().Border(wx.LEFT, 70))
        self.Layout()
        self.pnl.SetScrollbars(20, 20, 600, 400, yPos=400)
        wx.GetApp().Yield()
        
        isurban = self.multi_process_containment_tests()
        wx.EndBusyCursor()
        
        self.data['is_urban'] = isurban
        
        self.data.to_csv(os.path.splitext(self.picker_df.GetPath())[0] + '-UrbanAfricaLabelling.csv')
        
        self.button_begin.SetBackgroundColour('#b4eeb4')
        self.button_begin.SetLabel('All Done!\nCheck your working directory.')
        
    def OnFiltClick(self, event):
        if self.cb_filter_countries.IsChecked():
            self.col_names = self.data.columns
            self.dd_country_selector = wx.ComboBox(self.pnl, choices=self.col_names, size=wx.Size(200,25), value="Select the 'Country' column")
            self.sizer.Insert(10, self.dd_country_selector, wx.SizerFlags().Border(wx.LEFT, 70))
            self.button_validate_countries = wx.Button(self.pnl, label='Filter Africapolis', size=wx.Size(200,25))
            self.sizer.Insert(11, self.button_validate_countries, wx.SizerFlags().Border(wx.LEFT, 70))
            self.Bind(wx.EVT_BUTTON, self.validate_countries, id=self.button_validate_countries.GetId())
        else:
            self.sizer.Remove(10)
            self.dd_country_selector.Hide()
        self.sizer.Layout()
        
    def ProgCallback(self, key, result, dsk, state, id):
        self.prog += 1
        self.progress.SetLabel('\n|' + '-'*(self.prog-1) + '#' + '-'*(100-self.prog) + '| ' + str(self.prog) + '%\n')
        wx.GetApp().Yield()
        
#    def OnProgReport(self, event):
#        self.progress.SetLabel('|' + '#'*(event.data) + '_'*(100-event.data) + '| ' + str(event.data) + '%')


if __name__ == '__main__':
    freeze_support()
    # When this module is run (not imported) then create the app, the
    # frame, show it, and start the event loop.
    app = wx.App()
    frm = UAFrame()
    frm.Show()
    app.MainLoop()
