[Tuto](https://betterprogramming.pub/how-to-train-yolov5-for-recognizing-custom-game-objects-in-real-time-9d78369928a8)

En premier on vient prendre des captures d'ecran du jeux avec le script screenshot.py
On presse F quand on veut prendre une capture


Labélisation
On créé un fichier "label.txt" avec tout les labels possibles
Ensuite on utilise [Ce site](https://www.makesense.ai/) pour mettre des labels sur les images
On exporte ensuite sous format YOLO


DATASET
90% des images servirons a l'entrainement, les 10% restants serons la pour la validation
Pour cela on vas faire une arborésence
D:.
├───test_data
└───train_data
    ├───images
    │   ├───train
    │   └───val
    └───labels
        ├───train
        └───val

Dans le dossier train_data, nous allons avoir deux dossiers, un pour les images et l'autres pour les txt généré avec MakeSense
Dans chaqu'un de ces sous dossier, il y a un dossier avec les données d'entrainement et de validation
Puis dans le test_data, on met des captures d'ecran random
Enfin on créé un ready_data.yaml pour définir les labels ainsi que les chemins vers les images




INSTALLATION YOLOV5
git clone https://github.com/ultralytics/yolov5.git
cd yolov5
pip install -r requirements.txt

Installer cuda et pytorch
https://www.datasciencelearner.com/assertionerror-torch-not-compiled-with-cuda-enabled-fix/


TRAINING
Dans le dossier de YoloV5, on lance 
python train.py --img 640 --batch 2 --epochs 240 --data ../PROJECT/ready_data.yaml --weights yolov5s.pt --cache --device 0 --workers 2
Cela permet de lancer l'entrainement
Une fois fini, nous obtenons un fichier .pt, cela correspond au model généré (les poids)

TEST
python detect.py --weights runs/train/exp/weights/best.pt --img 640 --source ../PROJECT/ready_data/test_data/ --conf-thres 0.65
python detect.py --weights runs/train/exp/weights/best.pt --source ../test.mp4 --conf-thres 0.65



Conversion du model vers TensorRT pour une detection rapide (fast inference)
Installation de TensorRT pour nvidia https://docs.nvidia.com/deeplearning/tensorrt/install-guide/index.html
On lance l'export du model 
python export.py --weights ../best.pt --include engine --half --device 0
Nous obtenons un "best.engine"
