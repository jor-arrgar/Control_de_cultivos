class MayConv(str):
     
    def all_mayus(self, mayus=False):
        
        if mayus:
            return self.upper()
        else:
            return self
        
        
def traduce_booleans(bool_):
    
    if bool_:
        return 'SI'
    return 'NO'




def season_pie_chart(crop_surfaces):
    

    df = pd.DataFrame()
    df['SUPERFICIE'] = list(crop_surfaces.values())
    df['CULTIVO'] = list(crop_surfaces.keys())


    fig = go.Figure(data=[go.Pie(labels=df['CULTIVO'], values=df['SUPERFICIE'],
                                textinfo='percent',
                                insidetextorientation='radial'
                                )])
    fig.update_layout(width=300 , height=300)
    
    return fig , df.sort_values('SUPERFICIE' , ascending=False)


def merge_by_field(subfields_df):
    
    fields = set([subfield_name.split('_')[0] for subfield_name in subfields_df['Parcela']])
    
    fields_merged = {k: v for k, v in zip(fields, [{} for i in range(len(fields))])}
    
    for subfield, surface, crop in subfields_df[['Parcela', 'Superficie', 'Cultivo']].values:
        
        field = subfield.split('_')[0]
        
        fields_merged[field].update({crop:surface})
        
    return fields_merged