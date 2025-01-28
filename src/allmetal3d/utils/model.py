import torch
import torch.nn as nn
import torch.nn.functional as F


class WaterModel(nn.Module):
    def __init__(self):
        super(WaterModel, self).__init__()
        self.conv1 = nn.Conv3d(8, 40, 6, padding="same")
        self.conv2 = nn.Conv3d(40, 80, 6, padding="same")
        self.conv3 = nn.Conv3d(80, 200, 6, padding="same")
        self.conv4 = nn.Conv3d(200, 40, 6, padding="same")
        self.conv5 = nn.Conv3d(40, 32, 32, padding="same")
        self.conv6 = nn.Conv3d(32, 16, 6, padding="same")
        self.conv7 = nn.Conv3d(16, 1, 6, padding="same")
        self.dropout1 = nn.Dropout3d(0.2)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)

        x = F.relu(x)
        x = self.conv3(x)
        x = self.dropout1(x)
        x = F.relu(x)

        x = self.conv4(x)
        x = F.relu(x)

        x = self.conv5(x)
        x = F.relu(x)
        x = self.conv6(x)
        x = F.relu(x)

        x = self.conv7(x)
        x = torch.sigmoid(x)
        return x

class LocationModel(nn.Module):
    """Model with same padding without fingerprint"""

    def __init__(self):
        super(LocationModel, self).__init__()

        self.conv1 = nn.Conv3d(8, 40, 6, padding="same")
        self.conv2 = nn.Conv3d(40, 80, 6, padding="same")
        self.conv3 = nn.Conv3d(80, 200, 6, padding="same")
        self.conv4 = nn.Conv3d(200, 40, 6, padding="same")
        self.conv5 = nn.Conv3d(40, 32, 32, padding="same")
        self.conv6 = nn.Conv3d(32, 16, 6, padding="same")
        self.conv7 = nn.Conv3d(16, 1, 6, padding="same")
        self.dropout1 = nn.Dropout3d(0.2)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)

        x = F.relu(x)
        x = self.conv3(x)
        x = self.dropout1(x)
        x = F.relu(x)

        x = self.conv4(x)
        x = F.relu(x)

        x = self.conv5(x)
        x = F.relu(x)
        x = self.conv6(x)
        x = F.relu(x)

        x = self.conv7(x)
        x = torch.sigmoid(x)
        return x



metalions = ["ZN", "K", "NA", "CA", "MG", "FE", "CO", "CU", "MN", "NI", "FE2", "NoMetal"]

mapping_metals = {'NA':"Alkali", 'MG':"MG", 'K':"Alkali", 'NI':"NonZNTM", 'FE':"NonZNTM", 'NoMetal':"NoMetal", 'ZN':"ZN", 'MN':"NonZNTM", 'CU':"NonZNTM", 'FE2':"NonZNTM", 'CO':"NonZNTM", 'CA':"CA"}

mapping_metals_vals = ['Alkali', 'MG','CA','ZN', 'NonZNTM', 'NoMetal']

len_mapping_metals = len(set(mapping_metals.values()))

mapping = { ' pvp - pentagonal bipyramid with a vacancy (equatorial) (regular)\n':"pentagonal bipyramid",
 ' oct - octahedron (distorted)\n': "octahedron",
 'NoMetal':"NoMetal",
 ' pva - pentagonal bipyramid with a vacancy (axial) (distorted)\n':"pentagonal bipyramid",
 ' pbp - pentagonal bipyramid (distorted)\n':"pentagonal bipyramid",
 ' pvp - pentagonal bipyramid with a vacancy (equatorial) (distorted)\n':"pentagonal bipyramid",
 ' oct - octahedron (regular)\n' : "octahedron",
 ' spy - square pyramid (regular)\n': "square",
 ' bva - trigonal bipyramid with a vacancy (axial) (regular)\n': "other",
 ' trv - trigonal plane with a vacancy (regular)\n': "other",
 ' bva - trigonal bipyramid with a vacancy (axial) (distorted)\n' : "other",
 ' irr - Irregular geometry\n': "Irregular",
 ' sav - square antiprism with a vacancy (distorted)\n': "square",
 ' sqa - square antiprism (distorted)\n': "square",
 ' pbp - pentagonal bipyramid (regular)\n' : "pentagonal bipyramid",
 ' pyv - square pyramid with a vacancy (equatorial) (distorted)\n': "square",
 ' ctp - trigonal prism, square-face monocapped (distorted)\n' :"other",
 ' spv - square plane with a vacancy (distorted)\n' : "square",
 ' spy - square pyramid (distorted)\n' : "square",
 ' coc - octahedron, face monocapped (distorted)\n': "octahedron",
 ' bvp - trigonal bipyramid with a vacancy (equatorial) (distorted)\n': "other",
 ' spl - square plane (distorted)\n': "square",
 ' lin - linear (regular)\n' : "other",
 ' con - octahedron, face monocapped with a vacancy (non-capped face) (distorted)\n': "octahedron",
 ' tev - tetrahedron with a vacancy (regular)\n': "tetrahedron",
 ' bts - trigonal prism, square-face bicapped (distorted)\n': "other",
 ' pyv - square pyramid with a vacancy (equatorial) (regular)\n': "square",
 ' tev - tetrahedron with a vacancy (distorted)\n': "tetrahedron",
 ' hvp - hexagonal bipyramid with a vacancy (equatorial) (distorted)\n': "other",
 ' con - octahedron, face monocapped with a vacancy (non-capped face) (regular)\n': "octahedron",
 ' cof - octahedron, face monocapped with a vacancy (capped face) (distorted)\n': "octahedron",
 ' spv - square plane with a vacancy (regular)\n': "square",
 ' tpv - trigonal prism with a vacancy (regular)\n': "other",
 ' ctn - trigonal prism, square-face monocapped with a vacancy (non-capped edge) (distorted)\n': "other",
 ' coc - octahedron, face monocapped (regular)\n': "octahedron",
 ' ctf - trigonal prism, square-face monocapped with a vacancy (capped face) (distorted)\n':"other",
 ' pva - pentagonal bipyramid with a vacancy (axial) (regular)\n':"pentagonal bipyramid",
 ' tpr - trigonal prism (regular)\n':"other",
 ' tpv - trigonal prism with a vacancy (distorted)\n':"other",
 ' tbp - trigonal bipyramid (regular)\n':"other",
 ' tpr - trigonal prism (distorted)\n':"other",
 ' tet - tetrahedron (regular)\n':"tetrahedron",
 ' tet - tetrahedron (distorted)\n':"tetrahedron",
 ' tbp - trigonal bipyramid (distorted)\n':"other",
 ' tri - trigonal plane (regular)\n':"other",
 ' bvp - trigonal bipyramid with a vacancy (equatorial) (regular)\n':"other",
 ' spl - square plane (regular)\n': "square",
 ' tri - trigonal plane (distorted)\n':"other",
 ' hva - hexagonal bipyramid with a vacancy (axial) (distorted)\n':"other"
}
# { ' pvp - pentagonal bipyramid with a vacancy (equatorial) (regular)\n':"pentagonal bipyramid",
#  ' oct - octahedron (distorted)\n': "octahedron",
#  'NoMetal':"NoMetal",
#  ' pva - pentagonal bipyramid with a vacancy (axial) (distorted)\n':"pentagonal bipyramid",
#  ' pbp - pentagonal bipyramid (distorted)\n':"pentagonal bipyramid",
#  ' pvp - pentagonal bipyramid with a vacancy (equatorial) (distorted)\n':"pentagonal bipyramid",
#  ' oct - octahedron (regular)\n' : "octahedron",
#  ' spy - square pyramid (regular)\n': "square",
#  ' bva - trigonal bipyramid with a vacancy (axial) (regular)\n': "trigonal bipyramid",
#  ' trv - trigonal plane with a vacancy (regular)\n': "trigonal plane",
#  ' bva - trigonal bipyramid with a vacancy (axial) (distorted)\n' : "trigonal bipyramid",
#  ' irr - Irregular geometry\n': "Irregular",
#  ' sav - square antiprism with a vacancy (distorted)\n': "square",
#  ' sqa - square antiprism (distorted)\n': "square",
#  ' pbp - pentagonal bipyramid (regular)\n' : "pentagonal bipyramid",
#  ' pyv - square pyramid with a vacancy (equatorial) (distorted)\n': "square",
#  ' ctp - trigonal prism, square-face monocapped (distorted)\n' :"trigonal prism",
#  ' spv - square plane with a vacancy (distorted)\n' : "square",
#  ' spy - square pyramid (distorted)\n' : "square",
#  ' coc - octahedron, face monocapped (distorted)\n': "octahedron",
#  ' bvp - trigonal bipyramid with a vacancy (equatorial) (distorted)\n': "trigonal bipyramid",
#  ' spl - square plane (distorted)\n': "square",
#  ' lin - linear (regular)\n' : "other",
#  ' con - octahedron, face monocapped with a vacancy (non-capped face) (distorted)\n': "octahedron",
#  ' tev - tetrahedron with a vacancy (regular)\n': "tetrahedron",
#  ' bts - trigonal prism, square-face bicapped (distorted)\n': "trigonal prism",
#  ' pyv - square pyramid with a vacancy (equatorial) (regular)\n': "square",
#  ' tev - tetrahedron with a vacancy (distorted)\n': "tetrahedron",
#  ' hvp - hexagonal bipyramid with a vacancy (equatorial) (distorted)\n': "other",
#  ' con - octahedron, face monocapped with a vacancy (non-capped face) (regular)\n': "octahedron",
#  ' cof - octahedron, face monocapped with a vacancy (capped face) (distorted)\n': "octahedron",
#  ' spv - square plane with a vacancy (regular)\n': "square",
#  ' tpv - trigonal prism with a vacancy (regular)\n': "trigonal prism",
#  ' ctn - trigonal prism, square-face monocapped with a vacancy (non-capped edge) (distorted)\n': "trigonal prism",
#  ' coc - octahedron, face monocapped (regular)\n': "octahedron",
#  ' ctf - trigonal prism, square-face monocapped with a vacancy (capped face) (distorted)\n':"trigonal prism",
#  ' pva - pentagonal bipyramid with a vacancy (axial) (regular)\n':"pentagonal bipyramid",
#  ' tpr - trigonal prism (regular)\n':"trigonal prism",
#  ' tpv - trigonal prism with a vacancy (distorted)\n':"trigonal prism",
#  ' tbp - trigonal bipyramid (regular)\n':"trigonal bipyramid",
#  ' tpr - trigonal prism (distorted)\n':"trigonal prism",
#  ' tet - tetrahedron (regular)\n':"tetrahedron",
#  ' tet - tetrahedron (distorted)\n':"tetrahedron",
#  ' tbp - trigonal bipyramid (distorted)\n':"trigonal bipyramid",
#  ' tri - trigonal plane (regular)\n':"other",
#  ' bvp - trigonal bipyramid with a vacancy (equatorial) (regular)\n':"trigonal bipyramid",
#  ' spl - square plane (regular)\n': "square",
#  ' tri - trigonal plane (distorted)\n':"trigonal prism",
#  ' hva - hexagonal bipyramid with a vacancy (axial) (distorted)\n':"other"
# }


# mapping_vals_small = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']

mapping_vals_small = ['tetrahedron', 'octahedron', 'pentagonal bipyramid',   'square','Irregular', 'other','NoMetal']

len_geometry = len(set(mapping.values()))

mapping_vacancy = { ' pvp - pentagonal bipyramid with a vacancy (equatorial) (regular)\n':"vacancy",
 ' oct - octahedron (distorted)\n': "full",
 'NoMetal':"NoMetal",
 ' pva - pentagonal bipyramid with a vacancy (axial) (distorted)\n':"vacancy",
 ' pbp - pentagonal bipyramid (distorted)\n':"full",
 ' pvp - pentagonal bipyramid with a vacancy (equatorial) (distorted)\n':"vacancy",
 ' oct - octahedron (regular)\n' : "full",
 ' spy - square pyramid (regular)\n': "full",
 ' bva - trigonal bipyramid with a vacancy (axial) (regular)\n': "vacancy",
 ' trv - trigonal plane with a vacancy (regular)\n': "vacancy",
 ' bva - trigonal bipyramid with a vacancy (axial) (distorted)\n' : "vacancy",
 ' irr - Irregular geometry\n': "irregular",
 ' sav - square antiprism with a vacancy (distorted)\n': "vacancy",
 ' sqa - square antiprism (distorted)\n': "full",
 ' pbp - pentagonal bipyramid (regular)\n' : "full",
 ' pyv - square pyramid with a vacancy (equatorial) (distorted)\n': "vacancy",
 ' ctp - trigonal prism, square-face monocapped (distorted)\n' :"full",
 ' spv - square plane with a vacancy (distorted)\n' : "vacancy",
 ' spy - square pyramid (distorted)\n' : "full",
 ' coc - octahedron, face monocapped (distorted)\n': "full",
 ' bvp - trigonal bipyramid with a vacancy (equatorial) (distorted)\n': "vacancy",
 ' spl - square plane (distorted)\n': "full",
 ' lin - linear (regular)\n' : "full",
 ' con - octahedron, face monocapped with a vacancy (non-capped face) (distorted)\n': "vacancy",
 ' tev - tetrahedron with a vacancy (regular)\n': "vacancy",
 ' bts - trigonal prism, square-face bicapped (distorted)\n': "full",
 ' pyv - square pyramid with a vacancy (equatorial) (regular)\n': "vacancy",
 ' tev - tetrahedron with a vacancy (distorted)\n': "vacancy",
 ' hvp - hexagonal bipyramid with a vacancy (equatorial) (distorted)\n': "vacancy",
 ' con - octahedron, face monocapped with a vacancy (non-capped face) (regular)\n': "vacancy",
 ' cof - octahedron, face monocapped with a vacancy (capped face) (distorted)\n': "vacancy",
 ' spv - square plane with a vacancy (regular)\n': "vacancy",
 ' tpv - trigonal prism with a vacancy (regular)\n': "vacancy",
 ' ctn - trigonal prism, square-face monocapped with a vacancy (non-capped edge) (distorted)\n': "vacancy",
 ' coc - octahedron, face monocapped (regular)\n': "full",
 ' ctf - trigonal prism, square-face monocapped with a vacancy (capped face) (distorted)\n':"vacancy",
 ' pva - pentagonal bipyramid with a vacancy (axial) (regular)\n':"vacancy",
 ' tpr - trigonal prism (regular)\n':"full",
 ' tpv - trigonal prism with a vacancy (distorted)\n':"vacancy",
 ' tbp - trigonal bipyramid (regular)\n':"full",
 ' tpr - trigonal prism (distorted)\n':"full",
 ' tet - tetrahedron (regular)\n':"full",
 ' tet - tetrahedron (distorted)\n':"full",
 ' tbp - trigonal bipyramid (distorted)\n':"full",
 ' tri - trigonal plane (regular)\n':"full",
 ' bvp - trigonal bipyramid with a vacancy (equatorial) (regular)\n':"vacancy",
 ' spl - square plane (regular)\n': "full",
 ' tri - trigonal plane (distorted)\n':"full",
 ' hva - hexagonal bipyramid with a vacancy (axial) (distorted)\n':"vacancy"
}


len_vacancy = len(set(mapping_vacancy.values()))

vacancy_vals = ['irregular', 'full', 'vacancy', 'NoMetal']

class IdentityModel(nn.Module):
    """Model with same padding without fingerprint"""

    def __init__(self):
        super(IdentityModel, self).__init__()
        self.ConvID1 = nn.Conv3d(8, 60, 4)
        self.ConvID2 = nn.Conv3d(60, 100, 4)
        self.ConvID4 = nn.Conv3d(100, 80, 4)
        self.ConvID5 = nn.Conv3d(80, 30, 4)
        self.ConvID6 = nn.Conv3d(30,20,4)
        self.fc1_identity = nn.Linear(1281, 250)
        self.fc2_identity = nn.Linear(250, 100)
        self.fc3_identity = nn.Linear(100, len_mapping_metals)
        
        self.fc1_geometry = nn.Linear(1281, 250)
        self.fc2_geometry = nn.Linear(250, 100)
        self.fc3_geometry = nn.Linear(100, len_geometry)
        self.dropout1 = nn.Dropout3d(0.05)
        self.dropout2 = nn.Dropout(0.6)
        self.LeakyReLU = nn.LeakyReLU(0.2)

    def forward(self, input, probability):
        y = self.ConvID1(input)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.ConvID2(y)
        # y = self.dropout1(y)
        y = F.max_pool3d(y, 2)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.ConvID4(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.ConvID5(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.ConvID6(y)
        y = self.LeakyReLU(y)
        y = torch.flatten(y, 1)
        fingerprint = torch.cat([y, probability.unsqueeze(1)], dim=1)
        # identity
        y = self.fc1_identity(fingerprint)
        # y = self.dropout2(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.fc2_identity(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.fc3_identity(y)
        identity = F.softmax(y, dim=1)
        # vacancy
        # fingerprint2 = torch.cat([y, probability.unsqueeze(1),identity], dim=1)
       
        #geometry
        y = self.fc1_geometry(fingerprint)
        # y = self.dropout2(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.fc2_geometry(y)
        y = self.LeakyReLU(y)  # F.relu(y)
        y = self.fc3_geometry(y)
        geometry = F.softmax(y, dim=1)

        return identity, geometry

    # def __init__(self):
    #     super(IdentityModel, self).__init__()
    #     self.ConvID1 = nn.Conv3d(8, 60, 4)
    #     self.ConvID2 = nn.Conv3d(60, 80, 4)
    #     self.ConvID4 = nn.Conv3d(80, 60, 4)
    #     self.ConvID5 = nn.Conv3d(60, 30, 4)
    #     self.ConvID6 = nn.Conv3d(30,20,4)
    #     self.fc1_identity = nn.Linear(1281, 100)
    #     self.fc2_identity = nn.Linear(100, 30)
    #     self.fc3_identity = nn.Linear(30, len_mapping_metals)
    #     self.fc1_vacancy = nn.Linear(1281, 100)
    #     self.fc2_vacancy = nn.Linear(100, 30)
    #     self.fc3_vacancy = nn.Linear(30, len_vacancy)
    #     self.fc1_geometry = nn.Linear(1281, 100)
    #     self.fc2_geometry = nn.Linear(100, 30)
    #     self.fc3_geometry = nn.Linear(30, len_geometry)  #len_geometry  #  len_geometry
    #     self.dropout1 = nn.Dropout3d(0.2)
    #     self.dropout2 = nn.Dropout(0.2)
    #     self.LeakyReLU = nn.LeakyReLU(0.1)

    # def forward(self, input, probability):
    #     y = self.ConvID1(input)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.ConvID2(y)
    #     # y = self.dropout1(y)
    #     y = F.max_pool3d(y, 2)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.ConvID4(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.ConvID5(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.ConvID6(y)
    #     y = self.LeakyReLU(y)
    #     y = torch.flatten(y, 1)
    #     fingerprint = torch.cat([y, probability.unsqueeze(1)], dim=1)
    #     # identity
    #     y = self.fc1_identity(fingerprint)
    #     # y = self.dropout2(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc2_identity(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc3_identity(y)
    #     identity = F.softmax(y, dim=1)
    #     # vacancy
    #     y = self.fc1_vacancy(fingerprint)
    #     # y = self.dropout2(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc2_vacancy(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc3_vacancy(y)
    #     vacancy = F.softmax(y, dim=1)
    #     #geometry
    #     y = self.fc1_geometry(fingerprint)
    #     # y = self.dropout2(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc2_geometry(y)
    #     y = self.LeakyReLU(y)  # F.relu(y)
    #     y = self.fc3_geometry(y)
    #     geometry = F.softmax(y, dim=1)

    #     return identity, vacancy, geometry

# class Model(nn.Module):
#     """Model with same padding without fingerprint"""

#     def __init__(self):
#         super(Model, self).__init__()
#         metalions = [
#             "ZN",
#             "K",
#             "NA",
#             "CA",
#             "MG",
#             "FE2",
#             "FE",
#             "CO",
#             "CU",
#             "CU1" "MN",
#             "NI",
#         ]
#         self.conv1 = nn.Conv3d(8, 40, 6, padding="same")
#         self.conv2 = nn.Conv3d(40, 80, 6, padding="same")
#         self.conv3 = nn.Conv3d(80, 200, 6, padding="same")
#         self.conv4 = nn.Conv3d(200, 40, 6, padding="same")
#         self.conv5 = nn.Conv3d(40, 32, 32, padding="same")
#         self.conv6 = nn.Conv3d(32, 16, 6, padding="same")
#         self.conv7 = nn.Conv3d(16, len(metalions), 6, padding="same")
#         self.dropout1 = nn.Dropout3d(0.2)

#     def forward(self, x):
#         x = self.conv1(x)
#         x = F.relu(x)
#         x = self.conv2(x)

#         x = F.relu(x)
#         x = self.conv3(x)
#         x = self.dropout1(x)
#         x = F.relu(x)

#         x = self.conv4(x)
#         x = F.relu(x)

#         x = self.conv5(x)
#         x = F.relu(x)
#         x = self.conv6(x)
#         x = F.relu(x)

#         x = self.conv7(x)
#         x = torch.sigmoid(x)
#         return x
