# 增加ppd纸张尺寸
import os
from subprocess import Popen, PIPE

def getPrinters():
    '''
        返回打印机的名称
    '''
    p = Popen(['lpstat', '-a'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate()

    lines = output.decode().split('\n')
    _p = map(lambda x: x.split(' ')[0], lines)
    printers = [p for p in _p if p]
    return printers

new_paper ={
    '*DefaultPageSize':[
        '*PageSize 80x100mm": "<</PageSize[226.772 283.465]/ImagingBBox null>>setpagedevice"',
        '*PageSize 100x80mm": "<</PageSize[283.465 226.772 ]/ImagingBBox null>>setpagedevice"',
        '*PageSize 100x40mm": "<</PageSize[283.465 113.386 ]/ImagingBBox null>>setpagedevice"',
        '*PageSize 50x40mm": "<</PageSize[141.732 113.386 ]/ImagingBBox null>>setpagedevice"'
        ],
    '*DefaultPageRegion':[
        '*PageRegion 80x100mm": "<</PageSize[226.772 283.465]/ImagingBBox null>>setpagedevice"',
        '*PageRegion 100x80mm": "<</PageSize[283.465 226.772]/ImagingBBox null>>setpagedevice"',
        '*PageRegion 100x40mm": "<</PageSize[283.465 113.386]/ImagingBBox null>>setpagedevice"',
        '*PageRegion 50x40mm": "<</PageSize[141.732 113.386]/ImagingBBox null>>setpagedevice"'
    ],
    '*DefaultImageableArea':[
        '*ImageableArea 80x100mm": "0 0 226.772 283.465"',
        '*ImageableArea 100x80mm": "0 0  283.465 226.772"',
        '*ImageableArea 100x40mm": "0 0  283.465 113.386"',
        '*ImageableArea 50x40mm": "0 0  141.732 113.386"'
    ],
    '*DefaultPaperDimension':[
        '*PaperDimension 80x100mm": "226.772 283.465"',
        '*PaperDimension 100x80mm": "283.465 226.772"',
        '*PaperDimension 100x40mm": "283.465 113.386"',
        '*PaperDimension 50x40mm": "141.732 113.386"'
    ]
}

def mmToPoints(val):
    '''
    72 points = 1inch = 2.54cm
    只保留三位小数
    '''
    return int(val/25.4*72*1000)/1000

def makeNewPaper(width,length,name=''):
    if name=='':
        name = '{0}x{1}mm'.format(width,length)
    _w = mmToPoints(width)
    _l = mmToPoints(length)
    new_paper ={
        '*DefaultPageSize':[
            '*PageSize {0}": "<</PageSize[{1} {2}]/ImagingBBox null>>setpagedevice"'.format(name,_w,_l)
            ],
        '*DefaultPageRegion':[
            '*PageRegion {0}": "<</PageSize[{1} {2}]/ImagingBBox null>>setpagedevice"'.format(name,_w,_l)
        ],
        '*DefaultImageableArea':[
            '*ImageableArea {0}": "0 0 {1} {2}"'.format(name,_w,_l)
        ],
        '*DefaultPaperDimension':[
            '*PaperDimension {0}": "{1} {2}"'.format(name,_w,_l)
        ]
    }
    return new_paper

def main():
    if os.geteuid() != 0:
        print('必须使用root权限')
        return
    printers= getPrinters()
    for i,v in enumerate(printers):
        print(i,v)
    selected = int(input('请选择要编辑驱动的打印机?'))
    width = int(input('请输入纸张宽度mm:'))
    length = int(input('请输入纸张长度mm:'))
    name = input('输入纸张的名称不要输入中文(宽度x长度mm):')
    new_paper = makeNewPaper(width,length,name)
    with open('/etc/cups/ppd/{0}.ppd'.format(printers[selected]),'r+') as ppd:
        all_data = ppd.readlines()
        # 增加ppd新的尺寸
        for index, line in enumerate(all_data):
            for k in new_paper:
                if line.startswith(k):
                    all_data[index] = all_data[index].strip() + '\n' + '\n'.join(new_paper[k]) + '\n'
                # 删除重复的line
                for k,items in new_paper.items():
                    for v in items:
                        if line.strip() == v:
                            all_data[index] = ''
        ppd.seek(0)
        ppd.writelines([l for l in all_data if l])
        ppd.truncate()
        print('已完成')
if __name__ == "__main__":
    main()