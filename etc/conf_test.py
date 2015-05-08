DATABASES = {
    #'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'c2',
    #     'USER': 'ztgame_c2',
    #     'PASSWORD': 'ztgame_c2',
    #     'HOST': '172.30.250.21',
    #     'PORT': '',
    #},
    'default': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'mana',
         'USER': 'huming',
         'PASSWORD': 'huming',
         'HOST': '192.168.39.171',
         'PORT': '',
    },

    'KEYSTONE': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'keystone',
         'USER': 'keystone_admin',
         'PASSWORD': '6357a981729345ab',
         'HOST': '192.168.39.171',
         'PORT': '',
    },
    'KEYSTONE_Master': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'keystone',
         'USER': 'keystone_admin',
         'PASSWORD': '6357a981729345ab',
         'HOST': '192.168.39.171',
         'PORT': '3306',
    },
    #'Nanhui_nova': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'nova',
    #     'USER': 'ztgame',
    #     'PASSWORD': 'ztgame0001',
    #     'HOST': '172.30.250.21',
    #     'PORT': '',
    #},
    #'Nanhui_neutron': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'neutron_linux_bridge',
    #     'USER': 'ztgame',
    #     'PASSWORD': 'ztgame0001',
    #     'HOST': '172.30.250.21',
    #     'PORT': '',
    #},
    'shanghai_nova': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nova',
         'USER': 'root',
         #'PASSWORD': '22b4ba8149784ca5',
         'HOST': '192.168.39.171',
         'PORT': '',
    },
    'shanghai_neutron': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'neutron_linux_bridge',
         'USER': 'root',
         #'PASSWORD': '22b4ba8149784ca5',
         'HOST': '192.168.39.171',
         'PORT': '',
    },
    'beijing_nova': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nova',
         'USER': 'root',
         #'PASSWORD': '7424ff631df74810',
         'HOST': '192.168.39.175',
         'PORT': '',
    },
    'beijing_neutron': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'neutron_linux_bridge',
         'USER': 'root',
         #'PASSWORD': '03038432e1ba41ef',
         'HOST': '192.168.39.175',
         'PORT': '',
    },
}

REGIONS=(
        "shanghai",
        "beijing"
)


SYS_C2={
        "KS_USER":"admin",
        "KS_PWD":"123456",
        "tenant_id":"c521631f6ad742939bdfbb281bfeff5a",
        "KS_AUTH":"http://192.168.39.170:5000/v2.0",
        "KS_TENANT":"admin"
}

C2_AUTH_TOKEN={
        "168ba35f-f79e-4de7-876c-e58427d272ac":"admin",
        "f2298a33-11c5-4ecc-b76c-8db74d2b207c":"monitor",
	"c91f9406-de29-451c-92a8-7c9fd57443ee":"fengyu"
}

STATIC={
	"Salt_master":"172\.30\.250\.22",
	"Salt":"172.30.250.22",
	"Regions":REGIONS,
}


