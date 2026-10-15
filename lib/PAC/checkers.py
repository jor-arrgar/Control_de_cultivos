
crop_list = ['Ajo', 'Barbecho', 'Barbecho semillado', 'Cebada', 'Centeno', 'Colza', 'Garbanzo', 'Girasol',
             'Guisante', 'Lenteja' , 'Maiz', 'Patata', 'Remolacha', 'Trigo', 'Triticale', '']




class PAC_checker():
    
    crop_special_types = {'up_crops': ['Colza' , 'Girasol'],  # no incluye leguminosas
                          'leguminous_crops': ['Garbanzo' , 'Guisante' , 'Lenteja'],
                          'fallow': ['Barbecho', 'Barbecho semillado', 'Barbecho labrado']}    # deben incluirse en especies mejorante
    
    # Number of following same crop allowed => [1, 1, 1]  (3 años seguidos)
    not_allowed_time_series = []
    
    def __init__(self, fields_dataframe, exchange_dataframe):
        
        self.data = fields_dataframe
        self.exchange = exchange_dataframe
        
        self._crop_distribution()
        self._crop_time_series()
        self._calc_special_types_proportions()
        
    
    def _crop_distribution(self):
        
        crops = {}
        
        for field_name, surface, crop, exchanged in self.data[['Parcela', 'Superficie', 'Cultivo', 'Intercambio']].values:

            if not exchanged:
                if crop == 'None':
                    crop = 'Sin asignar'
                
                if crop not in crops.keys():
                    crop_surface = float(surface)
                
                else:
                    crop_surface = crops[crop] + float(surface)
                    
            elif exchanged == 1:
                exchanged_field = self.exchange[self.exchange['parcela original'] == field_name]

                crop = list(exchanged_field['cultivo'])[0]
                
                if crop == '':
                    crop = 'Sin asignar'
                
                if crop not in crops.keys():
                    crop_surface = list(exchanged_field['superficie'])[0]
                else:
                    crop_surface = crops[crop] + list(exchanged_field['superficie'])[0]

            crops.update({crop:crop_surface})

        total_surface = sum(crops.values())
        
        crops_percents = {}
        [crops_percents.update({crop: round(surface/total_surface, 2)}) for crop, surface in crops.items()]
        
        self.crops = crops
        self.crops_percents = crops_percents
        self.total_surface = round(total_surface, 2)
        
        self.crops_sorted = sorted(self.crops_percents.items(), key=lambda item: item[1])

        self.crops_sorted_dict = {}
        [self.crops_sorted_dict.update({crop:surface }) for (crop, surface) in self.crops_sorted[::-1]]
        
        
        
    def _crop_time_series(self):
        
        wrong_crop_series_fields = []

        
        for fields in self.data.values:
            
            field = fields[0]
            #past_crops_ = [crop.replace('[', '').replace(']', '').replace("'", '') for crop in list(set(fields[2:-1]))]
            past_crops = {}
            past_crops_lists = [eval(year) for year in fields[2:-2]]

            past_crops_list = []
            
            [past_crops_list.extend(year) for year in past_crops_lists if year is not None]
            all_crops = set(past_crops_list)
            [past_crops.update({crop:0}) for crop in all_crops]
            
            for year in past_crops_lists:
                if year is None:
                    continue
                for crop in year:
                    past_crops[crop] += 1


            actual_crop = fields[-1]
            
            if any([value >= 3 for value in past_crops.values()]) and (actual_crop in past_crops.keys()):
                wrong_crop_series_fields.append(field)

                
        self.wrong_crop_series = wrong_crop_series_fields

        
    def _calc_special_types_proportions(self):
        
        up_crops = 0
        leguminous = 0
        fallow = 0

        for crop, percent in self.crops_percents.items():
            
            if crop in self.crop_special_types['up_crops']:
                up_crops += percent
            
            elif crop in self.crop_special_types['leguminous_crops']:
                leguminous += percent
                
            elif crop in self.crop_special_types['fallow']:
                fallow += percent
                
        self.up_crops_percent = up_crops
        self.leguminous_percent = leguminous
        self.fallow_percent = fallow
        
        
    def return_info(self):
        
        return self.crops, self.crops_percents, self.wrong_crop_series
    
    
class Ecoregimen():
    
    def __init__(self, checker=PAC_checker):
        
        checker = checker
        

             


class PAC_2023_2027(PAC_checker):
    
    wrong_serie ='Más de 3 temporadas con el mismo cultivo en:\n'
    min2 = 'Mínimo 2 cultivos diferentes en la explotación'
    min3 = 'Mínimo 3 cultivos diferentes en la explotación'
    or_rotation = ' (o aplicar un 50\% de rotación)'
    main75 = 'El cultivo principal supera el 75\% de la superficie'
    main70 = 'El cultivo principal supera el 70\% de la superficie'
    mainSec90 = 'El cultivo principal junto con el secundario superan el 90% de la superficie'
    min_fallow = 'La superficie dedicada a elementos no productivos es menor del 4%'
    max_fallow = 'La superficie dedicada a elementos no productivos es mayor del 20%'
    min_legums = 'La superficie dedicada a especies leguminosas es menor del 5\%'
    min_upCrops = 'La superficie dedicada a especies mejorantes es menor del 10\%'
    
    eco345 = 'Ecorregimenes 3, 4 o 5 (Rotaciones y siembra directa)'
    p3 = 'Práctica nº 3 (Rotación de cultivos con especies mejorantes)'
    
    def __init__(self, fields_dataframe, exchange_dataframe):
        
        self.not_allowed_time_series = [1,1,1]
        super().__init__(fields_dataframe, exchange_dataframe)
        self.barbecho_surface = round(self.total_surface * 0.04, 2)
        self.ecoschemas = {}
        
        
        
    def return_info(self):
        return super().return_info()
    
    
    def check_conditionality(self):
        
        crops_sorted_tuples = list(self.crops_sorted_dict.items())

        unfullfilments = []
        # BCAM 7
            # Max 3 years with the same crop
        if self.wrong_crop_series != []:
            unfullfilments.append(f'BCAM7_series*{self.wrong_crop_series}')
        
            # Diversify crop surface
        if 10 < self.total_surface <= 20:
            if len(self.crops) < 2:
                unfullfilments.append('BCAM7_surf_10-20_N')
            if self.crops_sorted[-1][1] > 0.75:
                unfullfilments.append('BCAM7_surf_10-20_%')

        elif 20 < self.total_surface <= 30:
            if len(self.crops) < 2:
                unfullfilments.append('BCAM7_surf_20-30_N')
            if self.crops_sorted[-1][1] > 0.7:
                unfullfilments.append('BCAM7_surf_20-30_%')
            
        else:
            if len(self.crops) < 3:
                unfullfilments.append('BCAM7_surf_>30_N')
            if self.crops_sorted[0][1] > 0.7:
                unfullfilments.append('BCAM7_surf_>30_%1')
            if (self.crops_sorted[-1][1] + self.crops_sorted[-2][1]) > 0.9:
                unfullfilments.append('BCAM7_surf_>30_%1+2')
        
        # BCAM 8
            # >= 4% non-productive surface
        if self.fallow_percent < 0.04:
            unfullfilments.append('BCAM8_non-prod')
        
        if len(unfullfilments) == 0:
            # Condidionality correct
            return 0
        else:
            return unfullfilments
    
    def check_ecoregimen(self, ecoregimen):
        
        if ecoregimen in [3, 4, 5]: # Rotación y siembra directa en secano, secano húmedo y regadío


            
            crops_sorted_tuples = list(self.crops_sorted_dict.items())
            
            unfullfilments = []
            
            if self.total_surface < 10:
                #if rotation > 0.5:
                    #return 0
                #else:
                if len(self.crops) < 2:
                    unfullfilments.append('EcoReg_345_<10_N')  # Includes the rotation % error
                else:
                    if self.crops_percents[0][1] > 0.75:
                        unfullfilments.append('EcoReg_345_<10_%')
                
                    
            else:
                if len(self.crops) < 3:
                    unfullfilments.append('EcoReg_345_>10_N')
                
                if self.fallow_percent > 0.2:
                    unfullfilments.append('EcoReg_345_>10_maxFallow')
                    
                # Leguminous proportion > 5%
                if self.leguminous_percent < 0.05:
                    unfullfilments.append('EcoReg_345_>10_legums')
                
                # Up_crops proportion > 10% 
                if self.up_crops_percent + self.leguminous_percent < 0.1:
                    unfullfilments.append('EcoReg_345_>10_upCrops')
                
                # Rotation at least in 50%
                #if rotation < 0.5:
                    #return 'EcoReg_345_>10_rotation
            
            if len(unfullfilments) > 0:
                return unfullfilments
            else:
                return 0
                
                

        
    
  
        
    
    @staticmethod
    def error_code_translator(error_):
        
        if '*' in error_:
            split = error.split('*')
            fields = eval(split[1])
            error = split[0]
        else:
            fields = ''
            error = error_
        

        self = PAC_2023_2027
        
        errors = {'BCAM7_series': ('BCAM 7', self.wrong_serie + str(fields), None),
                  'BCAM7_surf_10-20_N':('BCAM 7', self.min2, None),
                  'BCAM7_surf_10-20_%':('BCAM 7', self.main75, None),
                  'BCAM7_surf_20-30_N':('BCAM 7', self.min2, None),
                  'BCAM7_surf_20-30_%':('BCAM 7', self.main70, None),
                  'BCAM7_surf_>30_N':('BCAM 7', self.min3, None),
                  'BCAM7_surf_>30_%1':('BCAM 7', self.main70, None),
                  'BCAM7_surf_>30_%1+2':('BCAM 7', self.mainSec90, None),
                  'BCAM8_non-prod':('BCAM 8', self.min_fallow, None),
                  'EcoReg_345_<10_N':(self.eco345, self.min2+self.or_rotation, self.p3),
                  'EcoReg_345_<10_%':(self.eco345, self.main75+self.or_rotation, self.p3),
                  'EcoReg_345_>10_N':(self.eco345, self.min3, self.p3),
                  'EcoReg_345_>10_maxFallow':(self.eco345, self.max_fallow, self.p3),
                  'EcoReg_345_>10_legums':(self.eco345, self.min_legums, self.p3),
                  'EcoReg_345_>10_upCrops':(self.eco345, self.min_upCrops, self.p3)
                  }
        
        main_, message, secondary = errors[error]
        
        return main_, message, secondary

    @staticmethod
    def error_messages_integrator(list_of_errors):
        
        if len(list_of_errors) == 0:
            return None, None
        
        self = PAC_2023_2027
        
        grouped_bcam = {'BCAM 7': [],
                        'BCAM 8': []}
        grouped_ecoreg = {self.eco345:{self.p3:[]}}
        
        bcam = False
        ecoreg = False
        
        for main_, message, secondary in list_of_errors:
            if main_[:4] == 'BCAM':
                grouped_bcam[main_].append(message)
                bcam = True
            elif main_[:13] == 'Ecorregimenes':
                grouped_ecoreg[main_][secondary].append(message)
                ecoreg = True
        
        if not bcam:
            return None, grouped_ecoreg
        if not ecoreg:
            return grouped_bcam, None
        return grouped_bcam, grouped_ecoreg
                
            

            
        