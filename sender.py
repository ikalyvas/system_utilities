import socket
import json
import struct

PORT_NUMBER=9999
dict_obj = { 
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': { 
        'standard': { 
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': { 
        'default': { 
            'level': 'CRITICAL',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': { 
        '': { 
            'handlers': ['default'],
            'level': 'CRITICAL',
            'propagate': True
        },
        'django.request': { 
            'handlers': ['default'],
            'level': 'WARN',
            'propagate': False
        },
    } 
}


d = json.dumps(dict_obj).encode('utf-8')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', PORT_NUMBER))
s.send(struct.pack('>L', len(d)))
s.send(d)
s.close()

