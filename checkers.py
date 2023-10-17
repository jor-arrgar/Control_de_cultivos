
crop_list = ['Ajo', 'Barbecho', 'Barbecho semillado', 'Cebada', 'Centeno', 'Colza', 'Garbanzo', 'Girasol',
             'Guisante', 'Lenteja' , 'Maiz', 'Patata', 'Remolacha', 'Trigo', 'Triticale', '']




class PAC_checker():
    
    crop_special_types = {'up_crops': ['Colza' , 'Girasol'],  # no incluye leguminosas
                          'leguminous_crops': ['Garbanzo' , 'Guisante' , 'Lenteja'],
                          'fallow': ['Barbecho', 'Barbecho semillado', 'Barbecho labrado']}    # deben incluirse en especies mejorante
    
    # Number of following same crop allowed => [1, 1, 1]  (3 años seguidos)
    not_allowed_time_series = []
    
    def __init__(self, fields_dataframe):
        
        self.data = fields_dataframe
        
        self._crop_distribution()
        self._crop_time_series()
        self._calc_special_types_proportions()
        
    
    def _crop_distribution(self):
        
        crops = {}
        
        for surface, crop in self.data[['Superficie', 'Cultivo']].values:
            
            if crop == 'None':
                crop = 'Sin asignar'
            
            if crop not in crops.keys():
                crop_surface = float(surface)
            
            else:
                crop_surface = crops[crop] + float(surface)
            
            crops.update({crop:crop_surface})

        total_surface = sum(crops.values())
        
        crops_percents = {}
        [crops_percents.update({crop: round(surface/total_surface, 2)}) for crop, surface in crops.items()]
        
        self.crops = crops
        self.crops_percents = crops_percents
        
        
    def _crop_time_series(self):
        
        wrong_crop_series_fields = []

        
        for fields in self.data.values:
            
            field = fields[0]
            
            
            #past_crops_ = [crop.replace('[', '').replace(']', '').replace("'", '') for crop in list(set(fields[2:-1]))]
            past_crops = {}
            past_crops_lists = [eval(year) for year in fields[2:-1]]

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
    
                      


class PAC_2023_2027(PAC_checker):
    
    def __init__(self, fields_dataframe):
        
        self.not_allowed_time_series = [1,1,1]
        super().__init__(fields_dataframe)
        
        
        
    def return_info(self):
        return super().return_info()
    
    
    def check_proportions(self):
        
        if self.fallow_percent < 0.04:
            return 7
        
        # Leguminous proportion > 5%
        if self.leguminous_percent < 0.05:
            return 1
        
        # Up_crops proportion > 10% 
        if self.up_crops_percent + self.leguminous_percent < 0.1:
            return 2
        
        
        crops_sorted = sorted(self.crops_percents.items(), key=lambda item: item[1])

        crops_sorted_dict = {}
        [crops_sorted_dict.update({crop:surface }) for (crop, surface) in crops_sorted[::-1]]

        # N crops >= 3
        if len(crops_sorted) < 3:
            return 3

        crops_sorted_tuples = list(crops_sorted_dict.items())
        
        # Main crop < 0.7
        if crops_sorted_tuples[0][1] >= 0.7:
            return 4
        
        # Secondary crop + Main crop < 0.9
        if crops_sorted_tuples[0][1] + crops_sorted_tuples[1][1] >= 0.9:
            return 5
        
        if self.wrong_crop_series != []:
            return 6
        
        
        # All test passed
        return 0
    
    @staticmethod
    def translate_error(error):
        
        errors = {0: 'Distribución correcta',
                  1: 'Leguminosas insuficientes (< 5%)',
                  2: 'Especies mejorantes insufieintes (< 10%)',
                  3: 'Numero insuficiente de cultivos diferentes (< 3)',
                  4: 'Cultivo mayoritario en exceso (> 70%)',
                  5: 'Suma de cultivo mayoritario y secundario en exceso (> 90%)',
                  6: '3 años seguidos con el mismo cultivo',
                  7: 'Barchecho insuficiente (< 4%)'}
        
        return errors[error]
    
        
    
        