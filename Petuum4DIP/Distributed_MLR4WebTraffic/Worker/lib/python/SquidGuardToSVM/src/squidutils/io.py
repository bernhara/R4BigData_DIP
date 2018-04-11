


def parseLogLine (log_line):
    
    split_squid_access_log_line = log_line.split()
    
    log_line_dict = {}
    field_index=0
    log_line_dict['ts.tu'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['tr'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['>a'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['Ss/Hs'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['<st'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['rm'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['ru'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['[un'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['Sh/<a'] = split_squid_access_log_line[field_index]; field_index += 1
    
    log_line_dict['mt'] = split_squid_access_log_line[field_index]; field_index += 1
    
    return log_line_dict
