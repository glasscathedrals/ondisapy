import datetime
import os
import sys
import tkinter as tk
import warnings
from tkinter import filedialog, messagebox

import ipywidgets as widgets
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ipywidgets import Button, HBox, Layout, VBox

sys.path.insert(0, os.path.join(os.path.dirname(os.getcwd()), 'scripts'))
from windroses import *

warnings.simplefilter("ignore")


class WidgetsMain(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        create_project_button = widgets.Button(description='Criar projeto', tooltip='Cria um novo projeto', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        create_project_button.on_click(self.create_project_button_click)
        load_project_button = widgets.Button(description='Importar projeto', tooltip='Importa o .csv de um projeto criado', layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        load_project_button.on_click(self.load_project_button_click)
        project_accordion = widgets.Accordion(
            children=[create_project_button, load_project_button])
        project_accordion.set_title(0, 'Criar projeto')
        project_accordion.set_title(1, 'Importar projeto')
        tab_contents = ['Projetos']
        tab_children = [project_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        return tab

    def create_project_button_click(self, b):

        self.project_dirs = self.create_project()

        return self.project_dirs

    def create_project(self):

        if not os.path.exists(os.path.join(self.path, 'proj')):

            os.makedirs(os.path.join(self.path, 'proj'))

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        create_project_asksaveasfilename_dir = filedialog.asksaveasfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Insira o nome desejado para seu projeto:", filetypes=[("Nome do projeto", ".")])

        if create_project_asksaveasfilename_dir == '':

            messagebox.showwarning("ondisapy", "Nenhum projeto criado.")

            return None

        else:

            if not os.path.exists(create_project_asksaveasfilename_dir):

                os.makedirs(create_project_asksaveasfilename_dir)

            project_data_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'data').replace('\\', '/'))
            project_waves_dir = (os.path.join(
                project_data_dir, 'wind_waves').replace('\\', '/'))
            project_winds_dir = (os.path.join(
                project_data_dir, 'wind_data').replace('\\', '/'))
            project_wind_fetchs_dir = (os.path.join(
                project_data_dir, 'wind_fetchs').replace('\\', '/'))
            project_img_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'img').replace('\\', '/'))
            project_grid_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'grid').replace('\\', '/'))
            project_dirs_list = [project_data_dir, project_waves_dir, project_winds_dir,
                                 project_wind_fetchs_dir, project_img_dir, project_grid_dir]

            print("Diretórios de projeto criados:")

            for i in project_dirs_list:

                try:

                    os.makedirs(i)

                    print("%s" % i)

                except OSError as Error:

                    if os.path.exists(i):

                        print("%s já existe." % i)

            project_file_dir = (os.path.join(
                create_project_asksaveasfilename_dir, 'dir.csv').replace('\\', '/'))

            if not os.path.exists(project_file_dir):

                project_name = os.path.basename(
                    create_project_asksaveasfilename_dir)
                project_dirs_list.append(project_name)
                project_dirs_dataframe = pd.DataFrame(
                    data={"dir": project_dirs_list})
                project_dirs_dataframe.to_csv(
                    project_file_dir, sep='\t', index=False, header=True, encoding='utf-8')

                messagebox.showinfo(
                    "ondisapy", "Projeto criado com sucesso:\n%s" % project_file_dir)

                print("\nProjeto criado:\n%s\n" % project_file_dir)

                return project_dirs_dataframe

            else:

                print("%s já existe.\n" % project_file_dir)

            print("\n")

    def load_project_button_click(self, b):

        self.project_dirs = self.load_project()

        return self.project_dirs

    def load_project(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_project_askopenfilename_dir = filedialog.askopenfilename(initialdir=os.path.join(
            self.path, 'proj'), title="Confirme o diretório de importação do arquivo '.csv' do seu projeto:", filetypes=[(".csv", "*.csv")])

        if load_project_askopenfilename_dir == '':

            messagebox.showwarning("ondisapy", "Nenhum projeto importado.")

            return None

        else:

            if not ('dir.csv') in str(load_project_askopenfilename_dir):

                messagebox.showwarning(
                    "ondisapy", "Erro: arquivo inválido.\nO arquivo realmente é um .csv de projeto criado?")

                return None

            else:

                project_dirs_dataframe = pd.read_csv(
                    load_project_askopenfilename_dir, sep='\t', engine='python', header=0, encoding='utf-8')

                messagebox.showinfo(
                    "ondisapy", "Projeto importado com sucesso:\n%s" % load_project_askopenfilename_dir)

                print("Projeto importado:\n%s\n" %
                      load_project_askopenfilename_dir)

            return (project_dirs_dataframe)


class WidgetsWindData(object):

    def __init__(self):

        self.path = os.path.dirname(os.getcwd())

    def display(self):

        load_csat3_wind_data_button = widgets.Button(description='Importar modelo de dados de ventos CSAT3',
                                                     tooltip='Importa um modelo de dados de ventos CSAT3 para leitura', layout=Layout(width='30%'), style={'description_width': 'initial'})
        load_csat3_wind_data_button.on_click(
            self.load_csat3_wind_data_button_click)
        load_windsonic_wind_data_button = widgets.Button(description='Importar modelo de dados de ventos Windsonic',
                                                         tooltip='Importa um modelo de dados de ventos Windsonic para leitura', layout=Layout(width='30%'), style={'description_width': 'initial'})
        load_windsonic_wind_data_button.on_click(
            self.load_windsonic_wind_data_button_click)
        self.height_adjustment_checkbox = widgets.Checkbox(
            description='Ajustar alturas', value=False, layout=Layout(width='30%'), style={'description_width': 'initial'})
        self.rl_checkbox = widgets.Checkbox(description='Utilizar RL', value=False, layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.rt_checkbox = widgets.Checkbox(description='Utilizar RT', value=False, layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.uz_checkbox = widgets.Checkbox(description='Utilizar U(z) (CSAT3)', value=False, layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.bins_int_text = widgets.IntText(description='Intervalos:', value=10, layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.step_int_text = widgets.IntText(description='Step:', value=1, layout=Layout(
            width='30%'), style={'description_width': 'initial'})
        self.speed_unit_text = widgets.Text(
            description='Unidade (m/s):', value='m/s', layout=Layout(width='30%'), style={'description_width': 'initial'})
        self.windrose_percentage_angle_float_text = widgets.FloatText(
            description='Ângulo (°):', value=33.75, layout=Layout(width='30%'), style={'description_width': 'initial'})
        wind_data_accordion = widgets.Accordion(
            children=[load_csat3_wind_data_button, load_windsonic_wind_data_button])
        wind_data_accordion.set_title(
            0, 'Importar modelo de dados de ventos CSAT3')
        wind_data_accordion.set_title(
            1, 'Importar modelo dados de ventos Windsonic')
        wind_adjustments_vbox = widgets.VBox(
            [self.height_adjustment_checkbox, self.rl_checkbox, self.rt_checkbox, self.uz_checkbox])
        wind_adjustments_accordion = widgets.Accordion(
            children=[wind_adjustments_vbox])
        wind_adjustments_accordion.set_title(
            0, 'Ajustes a serem incluídos nos cálculos de velocidades processedes')
        other_adjustments_accordion = widgets.Accordion(
            children=[self.windrose_percentage_angle_float_text, self.bins_int_text, self.step_int_text, self.speed_unit_text])
        other_adjustments_accordion.set_title(
            0, 'Ângulo para a rosa dos ventos')
        other_adjustments_accordion.set_title(1, 'Intervalos')
        other_adjustments_accordion.set_title(2, 'Step')
        other_adjustments_accordion.set_title(3, 'Unidade de velocidade')
        tab_contents = ['Dados de Ventos',
                        'Ajustes de Cálculo', 'Outros Ajustes']
        tab_children = [wind_data_accordion,
                        wind_adjustments_accordion, other_adjustments_accordion]
        tab = widgets.Tab()
        tab.children = tab_children

        for i in range(len(tab_children)):

            tab.set_title(i, tab_contents[i])

        display(tab)

    def load_csat3_wind_data_button_click(self, b):

        self.csat3_wind_data = self.load_csat3_wind_data()

    def load_csat3_wind_data(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_csat3_askopenfilename_dir = filedialog.askopenfilename(
            initialdir=self.path, title="Confirme o diretório de importação do arquivo '.csv' do seu modelo de dados de ventos CSAT3:", filetypes=[(".csv", "*.csv")])

        if load_csat3_askopenfilename_dir == '':

            messagebox.showwarning(
                "ondisapy", "Nenhum modelo de dados de ventos CSAT3 importado.")

            return None

        else:

            csat3_dataframe = pd.read_csv(
                load_csat3_askopenfilename_dir, sep=';', engine='python', encoding='utf-8', decimal=',')

            messagebox.showinfo(
                "ondisapy", "Modelo de dados de ventos CSAT3 importado com sucesso:\n%s" % load_csat3_askopenfilename_dir)

            print("Modelo de dados de ventos CSAT3 importado:\n%s\n" %
                  load_csat3_askopenfilename_dir)

            return csat3_dataframe

    def csat3_wind_data_dataframe(self, csat3_dataframe, project_dirs):

        self.csat3_dataframe = csat3_dataframe.copy()
        self.project_dirs = project_dirs

        if len(self.csat3_dataframe.filter(regex='Unnamed').columns) != 0:

            self.csat3_dataframe = self.csat3_dataframe[self.csat3_dataframe.columns.drop(
                list(self.csat3_dataframe.filter(regex='Unnamed')))]

        if False in self.csat3_dataframe.columns.isin(['TimeStamp', 'Ux', 'Uy', 'Uz', 'Ts', 'batt_volt', 'panel_temp', 'wnd_dir_csat3', 'wnd_dir_compass', 'height_measurement', 'RL', 'RT']):

            messagebox.showwarning(
                "ondisapy", "Modelo de dados de ventos CSAT3 com colunas nomeadas de forma diferente do modelo fornecido para uso.\nVerifique se seu arquivo .csv é proveniente do modelo correto para prosseguir com as análises.")

            return None

        else:

            self.csat3_dataframe[['Ux', 'Uy', 'Uz', 'Ts', 'batt_volt', 'panel_temp', 'wnd_dir_csat3', 'wnd_dir_compass', 'height_measurement', 'RL', 'RT']] = self.csat3_dataframe[[
                'Ux', 'Uy', 'Uz', 'Ts', 'batt_volt', 'panel_temp', 'wnd_dir_csat3', 'wnd_dir_compass', 'height_measurement', 'RL', 'RT']].astype('float64')
            csat3_dataframe_len = len(self.csat3_dataframe)
            self.csat3_dataframe = self.csat3_dataframe.dropna(
                subset=['TimeStamp', 'Ux', 'Uy', 'Uz', 'Ts', 'batt_volt', 'panel_temp', 'wnd_dir_csat3', 'wnd_dir_compass', 'height_measurement'])
            self.csat3_dataframe = self.csat3_dataframe.fillna(value='')
            csat3_dataframe_drop_na_len = len(self.csat3_dataframe)

            if self.uz_checkbox.value == False:

                if self.height_adjustment_checkbox.value == True:

                    processed_wind_speeds_list = [((((float(self.csat3_dataframe['Ux'][i]))**2)+((float(self.csat3_dataframe['Uy'][i]))**2))**(
                        0.5))*((10/self.csat3_dataframe['height_measurement'][i])**(1/7)) for i in self.csat3_dataframe.index]

                else:

                    processed_wind_speeds_list = [((((float(self.csat3_dataframe['Ux'][i]))**2)+(
                        (float(self.csat3_dataframe['Uy'][i]))**2))**(0.5)) for i in self.csat3_dataframe.index]

                if self.rl_checkbox.value == True:

                    processed_wind_speeds_list = [
                        i*self.csat3_dataframe['RL'][0] for i in processed_wind_speeds_list]

                if self.rt_checkbox.value == True:

                    processed_wind_speeds_list = [
                        i*self.csat3_dataframe['RT'][0] for i in processed_wind_speeds_list]

                self.csat3_dataframe['U'] = pd.Series(
                    processed_wind_speeds_list).values
                self.csat3_dataframe['TimeStamp'] = pd.to_datetime(
                    self.csat3_dataframe['TimeStamp'])

                print("Total de linhas sem valores utilizáveis removidas: %i de %i.\n" % (
                    csat3_dataframe_len-csat3_dataframe_drop_na_len, csat3_dataframe_len))

                self.csat3_dataframe = self.csat3_dataframe.iloc[::self.step_int_text.value]
                self.csat3_dataframe.reset_index(inplace=True, drop=True)
                self.csat3_dataframe.to_csv(os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
                ).replace(' ', '_')+'_csat3'+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

                display(self.csat3_dataframe)

                print("\nDados salvos em:\n%s\n" % os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
                ).replace(' ', '_')+'_csat3'+'.csv').replace('\\', '/').replace('\\', '/'))

                return self.csat3_dataframe

            elif self.uz_checkbox.value == True:

                if self.height_adjustment_checkbox.value == True:

                    processed_wind_speeds_list = [((((float(self.csat3_dataframe['Ux'][i]))**2)+((float(self.csat3_dataframe['Uy'][i]))**2)+((float(
                        self.csat3_dataframe['Uz'][i]))**2))**(0.5))*((10/self.csat3_dataframe['height_measurement'][i])**(1/7)) for i in self.csat3_dataframe.index]

                else:

                    processed_wind_speeds_list = [((((float(self.csat3_dataframe['Ux'][i]))**2)+((float(self.csat3_dataframe['Uy'][i]))**2)+(
                        (float(self.csat3_dataframe['Uz'][i]))**2))**(0.5)) for i in self.csat3_dataframe.index]

                if self.rl_checkbox.value == True:

                    processed_wind_speeds_list = [
                        i*self.csat3_dataframe['RL'][0] for i in processed_wind_speeds_list]

                if self.rt_checkbox.value == True:

                    processed_wind_speeds_list = [
                        i*self.csat3_dataframe['RT'][0] for i in processed_wind_speeds_list]

                self.csat3_dataframe['U'] = pd.Series(
                    processed_wind_speeds_list).values
                self.csat3_dataframe['TimeStamp'] = pd.to_datetime(
                    self.csat3_dataframe['TimeStamp'])

                print("Total de linhas sem valores utilizáveis removidas: %i de %i." % (
                    csat3_dataframe_len-csat3_dataframe_drop_na_len, csat3_dataframe_len))

                self.csat3_dataframe = self.csat3_dataframe.iloc[::self.step_int_text.value]
                self.csat3_dataframe.reset_index(inplace=True, drop=True)
                self.csat3_dataframe.to_csv(os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
                ).replace(' ', '_')+'_csat3'+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

                display(self.csat3_dataframe)

                print("\nDados salvos em:\n%s\n" % os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
                ).replace(' ', '_')+'_csat3'+'.csv').replace('\\', '/'))

                return self.csat3_dataframe

    def csat3_wind_data_windrose(self, csat3_dataframe, project_dirs):

        self.csat3_dataframe = csat3_dataframe
        self.project_dirs = project_dirs

        figure = plt.figure(figsize=(12, 12))
        axes = figure.add_axes([0, 0, 1, 1])
        axes.set_visible(False)
        csat3_windrose_dataframe = pd.DataFrame({'speed': pd.to_numeric(
            self.csat3_dataframe['U']), 'direction': pd.to_numeric(self.csat3_dataframe['wnd_dir_compass'])})
        axes = WindroseAxes.from_ax(fig=figure)
        axes.radii_angle = self.windrose_percentage_angle_float_text.value
        axes.bar(csat3_windrose_dataframe['direction'], csat3_windrose_dataframe['speed'],
                 normed=True, bins=self.bins_int_text.value, opening=0.7, edgecolor='white')
        legend_title = ('Velocidades (%s)') % self.speed_unit_text.value
        axes.legend(bbox_to_anchor=(1.3, 1), loc=1, title=legend_title)
        axes.grid(linewidth=0.5, antialiased=True)

        csat3_windrose_outputs_dir = os.path.join(
            self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

        try:

            os.makedirs(csat3_windrose_outputs_dir)

        except OSError as Error:

            if os.path.exists(csat3_windrose_outputs_dir):

                pass

        figure.savefig(os.path.join(csat3_windrose_outputs_dir, self.project_dirs['dir'][6].lower().replace(
            ' ', '_')+'_windrose_csat3'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight")
        plt.show()

        print("\nImagem salva em:\n%s\n" % os.path.join(csat3_windrose_outputs_dir,
                                                        self.project_dirs['dir'][6].lower().replace(' ', '_')+'_windrose_csat3'+'.png').replace('\\', '/'))

        return(figure, axes)

    def csat3_wind_frequencies(self, csat3_windrose, project_dirs):

        self.csat3_windrose = csat3_windrose
        self.project_dirs = project_dirs

        windrose_table = self.csat3_windrose[1]._info['table']
        windrose_frequencies = np.sum(windrose_table, axis=0)
        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        figure = plt.figure(figsize=(9, 9))
        axes = figure.add_axes([0, 0, 1, 1])
        plt.ylabel('Frequências percentuais (%)')
        plt.xlabel('Direção (°)')
        axes.bar(np.arange(16), windrose_frequencies, align='center',
                 tick_label=windrose_labels, facecolor='limegreen', zorder=3)
        axes_ticks = axes.get_yticks()
        axes.set_yticklabels(['{:.1f}%'.format(value) for value in axes_ticks])
        axes.grid(axis='y', zorder=0, linestyle='-', color='grey',
                  linewidth=0.5, antialiased=True, alpha=0.5)

        csat3_wind_frequencies_outputs_dir = os.path.join(
            self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

        try:

            os.makedirs(csat3_wind_frequencies_outputs_dir)

        except OSError as Error:

            if os.path.exists(csat3_wind_frequencies_outputs_dir):

                pass

        figure.savefig(os.path.join(csat3_wind_frequencies_outputs_dir, self.project_dirs['dir'][6].lower().replace(
            ' ', '_')+'_wind_frequencies_csat3'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight")
        plt.show()

        print("\nImagem salva em:\n%s\n" % os.path.join(csat3_wind_frequencies_outputs_dir,
                                                        self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_frequencies_csat3'+'.png').replace('\\', '/'))

    def csat3_wind_stats(self, csat3_dataframe, csat3_windrose, project_dirs):

        self.csat3_dataframe = csat3_dataframe
        self.csat3_windrose = csat3_windrose
        self.project_dirs = project_dirs

        windrose_directions_array = np.array(
            self.csat3_windrose[1]._info['dir'])
        windrose_directions_array = np.delete(windrose_directions_array, 0)
        windrose_directions_array = np.append(
            windrose_directions_array, 348.75)
        windrose_directions_list = []
        windrose_first_north_direction_split = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
            348.75, 360)]['U']
        windrose_second_north_direction_split = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
            0, 11.25)]['U']
        windrose_north_direction = pd.concat(
            [windrose_first_north_direction_split, windrose_second_north_direction_split], axis=0)
        windrose_directions_list.append([len(windrose_north_direction), windrose_north_direction.mean(
        ), windrose_north_direction.std(), windrose_north_direction.min(), windrose_north_direction.max()])

        for i, j in zip(windrose_directions_array[:-1], windrose_directions_array[1:]):

            sample_size = len(
                self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(i, j)]['U'])
            mean = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
                i, j)]['U'].mean()
            std = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
                i, j)]['U'].std()
            mininum = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
                i, j)]['U'].min()
            maximum = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
                i, j)]['U'].max()
            windrose_directions_list.append(
                [sample_size, mean, std, mininum, maximum])

        wind_stats_directions_dataframe = pd.DataFrame(
            windrose_directions_list)
        windrose_table = self.csat3_windrose[1]._info['table']
        windrose_frequencies = np.sum(windrose_table, axis=0)
        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        wind_stats_directions_dataframe['direction'] = windrose_labels
        wind_stats_directions_dataframe['frequency'] = windrose_frequencies
        wind_stats_directions_dataframe = wind_stats_directions_dataframe.round(
            decimals=2)
        wind_stats_directions_dataframe = wind_stats_directions_dataframe.rename(
            columns={0: 'sample_size', 1: 'mean', 2: 'std', 3: 'min', 4: 'max'})
        wind_stats_directions_dataframe = wind_stats_directions_dataframe[[
            'direction', 'sample_size', 'frequency', 'mean', 'std', 'min', 'max']]
        wind_stats_directions_dataframe.to_csv(os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
        ).replace(' ', '_')+'_wind_stats_csat3'+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

        display(wind_stats_directions_dataframe)

        print("\nDados salvos em:\n%s\n" % os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
        ).replace(' ', '_')+'_wind_stats_csat3'+'.csv').replace('\\', '/'))

    def csat3_wind_bins(self, csat3_dataframe, csat3_windrose, project_dirs):

        self.csat3_dataframe = csat3_dataframe
        self.csat3_windrose = csat3_windrose
        self.project_dirs = project_dirs

        windrose_directions_array = np.array(
            self.csat3_windrose[1]._info['dir'])
        windrose_directions_array = np.delete(windrose_directions_array, 0)
        windrose_directions_array = np.append(
            windrose_directions_array, 348.75)
        windrose_directions_list = []
        windrose_first_north_direction_split = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
            348.75, 360)]['U']
        windrose_second_north_direction_split = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
            0, 11.25)]['U']
        windrose_north_direction = pd.concat(
            [windrose_first_north_direction_split, windrose_second_north_direction_split], axis=0)
        windrose_directions_list.append(windrose_north_direction)

        for i, j in zip(windrose_directions_array[:-1], windrose_directions_array[1:]):

            windrose_direction_speeds = self.csat3_dataframe[self.csat3_dataframe['wnd_dir_compass'].between(
                i, j)]['U']
            windrose_directions_list.append(windrose_direction_speeds)

        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        windrose_directions_dict = {
            windrose_labels[i]: windrose_directions_list[i] for i in range(0, len(windrose_labels))}

        for i, j in windrose_directions_dict.items():

            figure = plt.figure(figsize=(9, 9))
            axes = figure.add_axes([0, 0, 1, 1])
            windrose_bins = self.csat3_windrose[1]._info['bins']
            windrose_formatted_bins = []

            for k in range(0, len(windrose_bins[:-2])):

                windrose_bins_interval = str(
                    '%.1f'+' – '+'%.1f') % (windrose_bins[k], windrose_bins[k+1])
                windrose_formatted_bins.append(windrose_bins_interval)

            windrose_last_bin = str('≧ '+'%.1f') % windrose_bins[-2]
            windrose_formatted_bins.append(windrose_last_bin)
            windrose_direction_speeds_dataframe = pd.DataFrame(j)
            windrose_direction_speeds_dataframe = windrose_direction_speeds_dataframe.groupby(pd.cut(
                windrose_direction_speeds_dataframe['U'], bins=windrose_bins, labels=windrose_formatted_bins, right=False)).count()
            windrose_direction_speeds_dataframe['%'] = [
                (k/sum(windrose_direction_speeds_dataframe['U']))*100 for k in windrose_direction_speeds_dataframe['U']]
            windrose_direction_speeds_dataframe['%'].plot(
                ax=axes, kind='bar', legend=False, colormap=None)
            axes.set_title('Direção %s' % i)
            axes.set_xlabel('Intervalos (%s)' % self.speed_unit_text.value)
            axes.set_ylabel('Porcentagem (%)')
            axes.autoscale(enable=True, axis='x', tight=None)

            for k in axes.get_xticklabels():

                k.set_rotation(45)

            bins_title = str('_wind_bins_%s' % i)

            csat3_wind_bins_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

            try:

                os.makedirs(csat3_wind_bins_outputs_dir)

            except OSError as Error:

                if os.path.exists(csat3_wind_bins_outputs_dir):

                    pass

            figure.savefig(os.path.join(csat3_wind_bins_outputs_dir, self.project_dirs['dir'][6].lower().replace(
                ' ', '_')+bins_title+'_csat3'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight", format='png')
            plt.show()

            print("\nImagem salva em:\n%s\n" % os.path.join(csat3_wind_bins_outputs_dir,
                                                            self.project_dirs['dir'][6].lower().replace(' ', '_')+bins_title+'_csat3'+'.png').replace('\\', '/'))

    def load_windsonic_wind_data_button_click(self, b):

        self.windsonic_wind_data = self.load_windsonic_wind_data()

    def load_windsonic_wind_data(self):

        sys._enablelegacywindowsfsencoding()

        root = tk.Tk()
        root.call('wm', 'attributes', '.', '-topmost', '1')
        root.withdraw()
        root.iconbitmap(os.path.join(self.path, 'logo.ico'))
        root.update_idletasks()

        load_windsonic_askopenfilename_dir = filedialog.askopenfilename(
            initialdir=self.path, title="Confirme o diretório de importação do arquivo '.csv' do seu modelo de dados de ventos Windsonic:", filetypes=[(".csv", "*.csv")])

        if load_windsonic_askopenfilename_dir == '':

            messagebox.showwarning(
                "ondisapy", "Nenhum modelo de dados de ventos Windsonic importado.")

            return None

        else:

            windsonic_dataframe = pd.read_csv(
                load_windsonic_askopenfilename_dir, sep=';', engine='python', encoding='utf-8', decimal=',')

            messagebox.showinfo(
                "ondisapy", "Modelo de dados de ventos Windsonic importado com sucesso:\n%s" % load_windsonic_askopenfilename_dir)

            print("Modelo Windsonic importado:\n%s\n" %
                  load_windsonic_askopenfilename_dir)

            return windsonic_dataframe

    def windsonic_wind_data_dataframe(self, windsonic_dataframe, project_dirs):

        self.windsonic_dataframe = windsonic_dataframe.copy()
        self.project_dirs = project_dirs

        if len(self.windsonic_dataframe.filter(regex='Unnamed').columns) != 0:

            self.windsonic_dataframe = self.windsonic_dataframe[self.windsonic_dataframe.columns.drop(
                list(self.windsonic_dataframe.filter(regex='Unnamed')))]

        if False in self.windsonic_dataframe.columns.isin(['TIMESTAMP', 'mean_wind_speed', 'mean_wind_direction', 'height_measurement', 'RL', 'RT']):

            messagebox.showwarning(
                "ondisapy", "Arquivo de dados de vento com colunas nomeadas de forma diferente do modelo fornecido para uso.\nVerifique se seu arquivo .csv é proveniente do modelo correto para prosseguir com as análises.")

            return None

        else:

            self.windsonic_dataframe[['mean_wind_speed', 'mean_wind_direction', 'height_measurement', 'RL', 'RT']] = self.windsonic_dataframe[[
                'mean_wind_speed', 'mean_wind_direction', 'height_measurement', 'RL', 'RT']].astype('float64')
            windsonic_dataframe_len = len(self.windsonic_dataframe)
            self.windsonic_dataframe = self.windsonic_dataframe.dropna(
                subset=['TIMESTAMP', 'mean_wind_speed', 'mean_wind_direction', 'height_measurement'])
            self.windsonic_dataframe = self.windsonic_dataframe.fillna(
                value='')
            windsonic_dataframe_drop_na_len = len(self.windsonic_dataframe)

            if self.height_adjustment_checkbox.value == True:

                processed_wind_speeds_list = [float(self.windsonic_dataframe['mean_wind_speed'][i]*(
                    (10/self.windsonic_dataframe['height_measurement'][i])**(1/7))) for i in self.windsonic_dataframe.index]

            else:

                processed_wind_speeds_list = [float(
                    self.windsonic_dataframe['mean_wind_speed'][i]) for i in self.windsonic_dataframe.index]

            if self.rl_checkbox.value == True:

                processed_wind_speeds_list = [
                    i*self.windsonic_dataframe['RL'][0] for i in processed_wind_speeds_list]

            if self.rt_checkbox.value == True:

                processed_wind_speeds_list = [
                    i*self.windsonic_dataframe['RT'][0] for i in processed_wind_speeds_list]

            self.windsonic_dataframe['U'] = pd.Series(
                processed_wind_speeds_list).values
            self.windsonic_dataframe['TIMESTAMP'] = pd.to_datetime(
                self.windsonic_dataframe['TIMESTAMP'])

            print("Total de linhas sem valores utilizáveis removidas: %i de %i.\n" % (
                windsonic_dataframe_len-windsonic_dataframe_drop_na_len, windsonic_dataframe_len))

            self.windsonic_dataframe = self.windsonic_dataframe.iloc[::self.step_int_text.value]
            self.windsonic_dataframe.reset_index(inplace=True, drop=True)
            self.windsonic_dataframe.to_csv(os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
            ).replace(' ', '_')+'_windsonic'+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

            display(self.windsonic_dataframe)

            print("\nDados salvos em:\n%s\n" % os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
            ).replace(' ', '_')+'_windsonic'+'.csv').replace('\\', '/'))

            return self.windsonic_dataframe

    def windsonic_wind_data_windrose(self, windsonic_dataframe, project_dirs):

        self.windsonic_dataframe = windsonic_dataframe
        self.project_dirs = project_dirs

        figure = plt.figure(figsize=(12, 12))
        axes = figure.add_axes([0, 0, 1, 1])
        axes.set_visible(False)
        windsonic_windrose_dataframe = pd.DataFrame({'speed': pd.to_numeric(
            self.windsonic_dataframe['U']), 'direction': pd.to_numeric(self.windsonic_dataframe['mean_wind_direction'])})
        axes = WindroseAxes.from_ax(fig=figure)
        axes.radii_angle = self.windrose_percentage_angle_float_text.value
        axes.bar(windsonic_windrose_dataframe['direction'], windsonic_windrose_dataframe['speed'],
                 normed=True, bins=self.bins_int_text.value, opening=0.7, edgecolor='white')
        legend_title = ('Velocidades (%s)') % self.speed_unit_text.value
        axes.legend(bbox_to_anchor=(1.3, 1), loc=1, title=legend_title)
        axes.grid(linewidth=0.5, antialiased=True)

        windsonic_windrose_outputs_dir = os.path.join(
            self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

        try:

            os.makedirs(windsonic_windrose_outputs_dir)

        except OSError as Error:

            if os.path.exists(windsonic_windrose_outputs_dir):

                pass

        figure.savefig(os.path.join(windsonic_windrose_outputs_dir, self.project_dirs['dir'][6].lower().replace(
            ' ', '_')+'_windrose_windsonic'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight")
        plt.show()

        print("\nImagem salva em:\n%s\n" % os.path.join(windsonic_windrose_outputs_dir,
                                                        self.project_dirs['dir'][6].lower().replace(' ', '_')+'_windrose_windsonic'+'.png').replace('\\', '/'))

        return(figure, axes)

    def windsonic_wind_frequencies(self, windsonic_windrose, project_dirs):

        self.windsonic_windrose = windsonic_windrose
        self.project_dirs = project_dirs

        windrose_table = self.windsonic_windrose[1]._info['table']
        windrose_frequencies = np.sum(windrose_table, axis=0)
        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        figure = plt.figure(figsize=(9, 9))
        axes = figure.add_axes([0, 0, 1, 1])
        plt.ylabel('Frequências percentuais (%)')
        plt.xlabel('Direção (°)')
        axes.bar(np.arange(16), windrose_frequencies, align='center',
                 tick_label=windrose_labels, facecolor='limegreen', zorder=3)
        axes_ticks = axes.get_yticks()
        axes.set_yticklabels(['{:.1f}%'.format(value) for value in axes_ticks])
        axes.grid(axis='y', zorder=0, linestyle='-', color='grey',
                  linewidth=0.5, antialiased=True, alpha=0.5)

        windsonic_wind_frequencies_outputs_dir = os.path.join(
            self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

        try:

            os.makedirs(windsonic_wind_frequencies_outputs_dir)

        except OSError as Error:

            if os.path.exists(windsonic_wind_frequencies_outputs_dir):

                pass

        figure.savefig(os.path.join(windsonic_wind_frequencies_outputs_dir, self.project_dirs['dir'][6].lower().replace(
            ' ', '_')+'_wind_frequencies_windsonic'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight")
        plt.show()

        print("\nImagem salva em:\n%s\n" % os.path.join(windsonic_wind_frequencies_outputs_dir,
                                                        self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_frequencies_windsonic'+'.png').replace('\\', '/'))

    def windsonic_wind_stats(self, windsonic_dataframe, windsonic_windrose, project_dirs):

        self.windsonic_dataframe = windsonic_dataframe
        self.windsonic_windrose = windsonic_windrose
        self.project_dirs = project_dirs

        windrose_directions_array = np.array(
            self.windsonic_windrose[1]._info['dir'])
        windrose_directions_array = np.delete(windrose_directions_array, 0)
        windrose_directions_array = np.append(
            windrose_directions_array, 348.75)
        windrose_directions_list = []
        windrose_first_north_direction_split = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
            348.75, 360)]['U']
        windrose_second_north_direction_split = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
            0, 11.25)]['U']
        windrose_north_direction = pd.concat(
            [windrose_first_north_direction_split, windrose_second_north_direction_split], axis=0)
        windrose_directions_list.append([len(windrose_north_direction), windrose_north_direction.mean(
        ), windrose_north_direction.std(), windrose_north_direction.min(), windrose_north_direction.max()])

        for i, j in zip(windrose_directions_array[:-1], windrose_directions_array[1:]):

            sample_size = len(
                self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(i, j)]['U'])
            mean = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
                i, j)]['U'].mean()
            std = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
                i, j)]['U'].std()
            mininum = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
                i, j)]['U'].min()
            maximum = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
                i, j)]['U'].max()
            windrose_directions_list.append(
                [sample_size, mean, std, mininum, maximum])

        wind_stats_directions_dataframe = pd.DataFrame(
            windrose_directions_list)
        windrose_table = self.windsonic_windrose[1]._info['table']
        windrose_frequencies = np.sum(windrose_table, axis=0)
        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        wind_stats_directions_dataframe['direction'] = windrose_labels
        wind_stats_directions_dataframe['frequency'] = windrose_frequencies
        wind_stats_directions_dataframe = wind_stats_directions_dataframe.round(
            decimals=2)
        wind_stats_directions_dataframe = wind_stats_directions_dataframe.rename(
            columns={0: 'sample_size', 1: 'mean', 2: 'std', 3: 'min', 4: 'max'})
        wind_stats_directions_dataframe = wind_stats_directions_dataframe[[
            'direction', 'sample_size', 'frequency', 'mean', 'std', 'min', 'max']]
        wind_stats_directions_dataframe.to_csv(os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
        ).replace(' ', '_')+'_wind_stats_windsonic'+'.csv').replace('\\', '/'), encoding='utf-8', sep=';', index=True)

        display(wind_stats_directions_dataframe)

        print("\nDados salvos em:\n%s\n" % os.path.join(self.project_dirs['dir'][2], self.project_dirs['dir'][6].lower(
        ).replace(' ', '_')+'_wind_stats_windsonic'+'.csv').replace('\\', '/'))

    def windsonic_wind_bins(self, windsonic_dataframe, windsonic_windrose, project_dirs):

        self.windsonic_dataframe = windsonic_dataframe
        self.windsonic_windrose = windsonic_windrose
        self.project_dirs = project_dirs

        windrose_directions_array = np.array(
            self.windsonic_windrose[1]._info['dir'])
        windrose_directions_array = np.delete(windrose_directions_array, 0)
        windrose_directions_array = np.append(
            windrose_directions_array, 348.75)
        windrose_directions_list = []
        windrose_first_north_direction_split = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
            348.75, 360)]['U']
        windrose_second_north_direction_split = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
            0, 11.25)]['U']
        windrose_north_direction = pd.concat(
            [windrose_first_north_direction_split, windrose_second_north_direction_split], axis=0)
        windrose_directions_list.append(windrose_north_direction)

        for i, j in zip(windrose_directions_array[:-1], windrose_directions_array[1:]):

            windrose_direction_speeds = self.windsonic_dataframe[self.windsonic_dataframe['mean_wind_direction'].between(
                i, j)]['U']
            windrose_directions_list.append(windrose_direction_speeds)

        windrose_labels = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE',
                           'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        windrose_directions_dict = {
            windrose_labels[i]: windrose_directions_list[i] for i in range(0, len(windrose_labels))}

        for i, j in windrose_directions_dict.items():

            figure = plt.figure(figsize=(9, 9))
            axes = figure.add_axes([0, 0, 1, 1])
            windrose_bins = self.windsonic_windrose[1]._info['bins']
            windrose_formatted_bins = []

            for k in range(0, len(windrose_bins[:-2])):

                windrose_bins_interval = str(
                    '%.1f'+' – '+'%.1f') % (windrose_bins[k], windrose_bins[k+1])
                windrose_formatted_bins.append(windrose_bins_interval)

            windrose_last_bin = str('≧ '+'%.1f') % windrose_bins[-2]
            windrose_formatted_bins.append(windrose_last_bin)
            windrose_direction_speeds_dataframe = pd.DataFrame(j)
            windrose_direction_speeds_dataframe = windrose_direction_speeds_dataframe.groupby(pd.cut(
                windrose_direction_speeds_dataframe['U'], bins=windrose_bins, labels=windrose_formatted_bins, right=False)).count()
            windrose_direction_speeds_dataframe['%'] = [
                (k/sum(windrose_direction_speeds_dataframe['U']))*100 for k in windrose_direction_speeds_dataframe['U']]
            windrose_direction_speeds_dataframe['%'].plot(
                ax=axes, kind='bar', legend=False, colormap=None)
            axes.set_title('Direção %s' % i)
            axes.set_xlabel('Intervalos (%s)' % self.speed_unit_text.value)
            axes.set_ylabel('Porcentagem (%)')
            axes.autoscale(enable=True, axis='x', tight=None)

            for k in axes.get_xticklabels():

                k.set_rotation(45)

            bins_title = str('_wind_bins_%s' % i)

            windsonic_wind_bins_outputs_dir = os.path.join(
                self.project_dirs['dir'][4], self.project_dirs['dir'][6].lower().replace(' ', '_')+'_wind_data')

            try:

                os.makedirs(windsonic_wind_bins_outputs_dir)

            except OSError as Error:

                if os.path.exists(windsonic_wind_bins_outputs_dir):

                    pass

            figure.savefig(os.path.join(windsonic_wind_bins_outputs_dir, self.project_dirs['dir'][6].lower().replace(
                ' ', '_')+bins_title+'_windsonic'+'.png').replace('\\', '/'), dpi=600, frameon=False, bbox_inches="tight", format='png')
            plt.show()

            print("\nImagem salva em:\n%s\n" % os.path.join(windsonic_wind_bins_outputs_dir,
                                                            self.project_dirs['dir'][6].lower().replace(' ', '_')+bins_title+'_windsonic'+'.png').replace('\\', '/'))
