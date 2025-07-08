
bash
python3 -m venv venv
source venv/bin/activate

bash
pip install ezdxf pandas numpy matplotlib shapely

#save my "POINTS AND LINES.dxf" fill in what you need

bash
python extract_dxf_data.py

bash
python panelize.py

bash
tributary.py



