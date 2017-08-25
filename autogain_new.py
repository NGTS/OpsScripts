import os
import argparse as ap
import numpy as np

def argParse():
    p = ap.ArgumentParser()
    p.add_argument('camera', help='camera ID')
    p.add_argument('pag', help='Pre amp gain', choices=[1, 2, 4], type=int)
    p.add_argument('outdir', help='location to put files')
    p.add_argument('t1', type=int, help='lower t_exp')
    p.add_argument('t2', type=int, help='upper t_exp')
    return p.parse_args()

if __name__ == "__main__":
    args = argParse()
    imseq_dir = '/home/ops/ngts/imsequence'
    times = np.arange(args.t1, args.t2+1)
    print(times)
    os.chdir(imseq_dir)
    # take 2 biases first
    comm_b = ("./imsequence --temperature -70 --fan full --gain {}"
              " --holdtemp --fastcool --sequence 2b --outdir {}").format(args.pag,
                                                                         args.outdir)
    os.system(comm_b)
    os.system('mv {}/UNKNOWN_0000_BIAS.fits {}/{}_PAG{}_{:02d}_1.fits'.format(args.outdir,
                                                                              args.outdir,
                                                                              args.camera,
                                                                              args.pag,
                                                                              0))
    os.system('mv {}/UNKNOWN_0001_BIAS.fits {}/{}_PAG{}_{:02d}_2.fits'.format(args.outdir,
                                                                              args.outdir,
                                                                              args.camera,
                                                                              args.pag,
                                                                              0))
    # do the science images
    for i, time in enumerate(times):
        comm = ("./imsequence --temperature -70 --fan full --gain {}"
                " --holdtemp --fastcool --sequence 'i1;2i{}' --outdir {}").format(args.pag,
                                                                                  time,
                                                                                  args.outdir)
        os.system(comm)
        os.system('mv {}/UNKNOWN_0000_IMAGE.fits {}/{}_PAG{}_01_{}.fits'.format(args.outdir,
                                                                                    args.outdir,
                                                                                    args.camera,
                                                                                    args.pag,
                                                                                    time,
                                                                                    i+1))
        os.system('mv {}/UNKNOWN_0001_IMAGE.fits {}/{}_PAG{}_{:02d}_1.fits'.format(args.outdir,
                                                                                   args.outdir,
                                                                                   args.camera,
                                                                                   args.pag,
                                                                                   time))
        os.system('mv {}/UNKNOWN_0002_IMAGE.fits {}/{}_PAG{}_{:02d}_2.fits'.format(args.outdir,
                                                                                   args.outdir,
                                                                                   args.camera,
                                                                                   args.pag,
                                                                                   time))
