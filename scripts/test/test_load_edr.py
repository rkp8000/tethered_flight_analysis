from data_handling import load_edr


FNAME = '/Users/rkp/Dropbox/arena_data/edr_files_visual_expt/150415_insect2_just_visual.EDR'

data, file_start, col_names, header = load_edr(FNAME, dt=.001)

print 'data.shape: (%d, %d)' % data.shape
print 'file_start: %s' % file_start.strftime('%c')
print 'col_names: [%s]' % ', '.join(col_names)
print 'header size: %d' % len(header)

print 'DT: %f' % header['DT']