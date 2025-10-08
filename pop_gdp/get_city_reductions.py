# Usage: python -m pop_gdp.get_city_reductions

import ee
    
ee.Initialize(project='ee-shruti-jain-90')

def reduce_region(raster, feature, reducer=ee.Reducer.sum()): 
    val = raster.reduceRegion(
        reducer=reducer,
        geometry=feature.geometry(),
        scale=raster.projection().nominalScale(),
        maxPixels=1e9
    )
    return ee.Feature(feature.geometry(), val).copyProperties(feature)

def export_features(features, item, export_to='drive'):
    
    if export_to=='drive':
        task = ee.batch.Export.table.toDrive(
            collection=features.map(lambda f: f.setGeometry(None)),
            description=item,
            fileNamePrefix=item
        )
    else:
        task = ee.batch.Export.table.toAsset(
            collection=features,
            description=item,
            assetId=f'projects/ee-shruti-jain-90/assets/cities_diets/reductions/{item}'
        )
    task.start()
    return task

# def get_country_name(features, gaul, uid):

#     def _lookup(f, uid):
#         matched = ee.Feature(f.get('matched'))
#         name = ee.Algorithms.If(matched, matched.get('ADM0_NAME'), None)
#         code = ee.Algorithms.If(matched, matched.get('ADM0_CODE'), None)
#         return ee.Feature(None, {uid: f.get(uid),
#                                  'ADM0_NAME': name,
#                                  'ADM0_CODE': code})

#     def _attach_from_lookup(f):
#         matched = ee.Feature(f.get('match'))  
#         name = ee.Algorithms.If(matched, matched.get('ADM0_NAME'), None)
#         code = ee.Algorithms.If(matched, matched.get('ADM0_CODE'), None)
#         prop_names = ee.List(f.propertyNames()).remove('match')
#         props = f.toDictionary(prop_names).set('ADM0_NAME', name).set('ADM0_CODE', code)
#         return ee.Feature(f.geometry(), props)
    
#     centroids = features.map(lambda f: ee.Feature(f.geometry().centroid(maxError=100)).copyProperties(f, [uid]))

#     intersects = ee.Filter.intersects(leftField='.geo', rightField='.geo')
#     saveFirst = ee.Join.saveFirst('matched')
#     joined_pts = saveFirst.apply(centroids, gaul, intersects)
#     centroids = ee.FeatureCollection(joined_pts.map(lambda f: _lookup(f, uid)))

#     equals_filter = ee.Filter.equals(leftField=uid, rightField=uid)
#     saveFirstAttr = ee.Join.saveFirst('match')
#     joined_attr = saveFirstAttr.apply(features, centroids, equals_filter)
#     features = ee.FeatureCollection(joined_attr.map(_attach_from_lookup))
#     return features


# def get_country_name(feature, gaul):
#     pt = ee.Feature(feature).geometry().centroid(100)
#     containing = gaul.filterBounds(pt).first()
#     name = ee.Algorithms.If(containing, ee.Feature(containing).get('ADM0_NAME'), None)
#     code = ee.Algorithms.If(containing, ee.Feature(containing).get('ADM0_CODE'), None)
#     return feature.set({'ADM0_NAME': name, 'ADM0_CODE': code})

if __name__ == '__main__':
    
    cities_arcgis = ee.FeatureCollection('projects/ee-shruti-jain-90/assets/cities_diets/city_poly/World_Urban_Areas_arcgis')
    cities_guppd = ee.FeatureCollection('projects/ee-shruti-jain-90/assets/cities_diets/city_poly/urban_settlements_guppd')
    cities_guppd = cities_guppd.filter(ee.Filter.eq('SMOD_LEVEL', '30'))

    # gaul = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level0") # country boundaries to assign country names to cities   

    # cities_arcgis = get_country_name(cities_arcgis, gaul, 'FID')
    # cities_guppd = get_country_name(cities_guppd, gaul, 'SOMD_ID

    # cities_arcgis = ee.FeatureCollection(cities_arcgis.map(lambda feature: get_country_name(feature, gaul)))
    # cities_guppd = ee.FeatureCollection(cities_guppd.map(lambda feature: get_country_name(feature, gaul)))

    #worldpop
    pop_imgcol = ee.ImageCollection('projects/ee-shruti-jain-90/assets/cities_diets/worldpop/age_sex_structures')
    pop = pop_imgcol.toBands()
    pop_red = cities_guppd.map(lambda feature: reduce_region(pop, feature))
    export_features(pop_red, 'population_age_sex_guppd', export_to='drive')
    export_features(pop_red, 'population_age_sex_guppd', export_to='asset')

    pop_red = cities_arcgis.map(lambda feature: reduce_region(pop, feature))
    export_features(pop_red, 'population_age_sex_arcgis', export_to='drive')
    export_features(pop_red, 'population_age_sex_arcgis', export_to='asset')

    # gdp
    gdp = ee.Image("projects/ee-shruti-jain-90/assets/cities_diets/gdp/rast_gdpTot_1990_2020_30arcsec")

    gdp_red = cities_guppd.map(lambda feature: reduce_region(gdp, feature))
    export_features(gdp_red, 'gdp_guppd', export_to='drive')
    export_features(gdp_red, 'gdp_guppd', export_to='asset')

    gdp_red = cities_arcgis.map(lambda feature: reduce_region(gdp, feature))
    export_features(gdp_red, 'gdp_arcgis', export_to='drive')
    export_features(gdp_red, 'gdp_arcgis', export_to='asset')

    
    

