import shutil
import pathlib
src_base = pathlib.Path('project_domains/data-mining/Predicting Second Hand Cars Price using Machine Learning Algorithms/Source Code')
dest_base = pathlib.Path('.')

src_app = src_base / 'car_price_app'
dest_app = dest_base / 'car_price_app'
if dest_app.exists():
    print('destination car_price_app exists, skipping copy')
else:
    shutil.copytree(src_app, dest_app)
    print('copied car_price_app')

for name in ['apriori_analysis.py', 'dataset_loader.py']:
    src = src_base / name
    dest = dest_base / name
    if dest.exists():
        print(f'{name} already exists, skipping')
    else:
        shutil.copy2(src, dest)
        print(f'copied {name}')
