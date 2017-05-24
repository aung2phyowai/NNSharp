import json
import numpy as np


class JSONwriter:

    def __init__(self, model, fname):
        self.model = model
        self.fname = fname
        self.json_string = ""
        self.idx = 0

    def save(self):
        self.__model_to_JSON(self.model)
        self.__save_json_string()
    
    
    def __model_to_JSON(self, model):
        # Initialization
        conf = model.get_config()
        md = {'model_type':'Sequential'}
        md['descriptors'] = []
        
        # Find the descriptors and transform the weights
        weights = []
        w_org = model.get_weights()
        
        # First the input layer
        inp_sizes = conf[0]['config']['batch_input_shape']
        layer_input = {}
        if len(inp_sizes) == 3:
            layer_input = {'layer':'Input2D', 'height':1, 'width':inp_sizes[1], 'channel':inp_sizes[2]}
        elif len(inp_sizes) == 4:
            layer_input = {'layer':'Input2D', 'height':inp_sizes[1], 'width':inp_sizes[2], 'channel':inp_sizes[3]}
        elif len(inp_sizes) == 2:
            layer_input = {'layer':'Input2D', 'height':1, 'width':1, 'channel':inp_sizes[1]}
        if inp_sizes[0] is None:
            layer_input['batch'] = 1
        else:
            layer_input['batch'] = inp_sizes[0]
        md['descriptors'].append(layer_input)
            
        # Remaining layers
        num = len(conf)
        for idx in range(0, num):
            layer = self.__get_layer(conf[idx])
            self.__get_weight(weights, w_org, conf[idx])
            for l in layer:
                md['descriptors'].append(l)
            
        md['weights'] = weights
        
        # Create JSON string
        self.json_string = json.JSONEncoder().encode(md)
    
    def __get_layer(self, layer_descr):
        layers = []
        name = layer_descr['class_name']
        
        if 'Conv1D' == name:
            k_s = layer_descr['config']['kernel_size'][0]
            k_num = layer_descr['config']['filters']
            stride = layer_descr['config']['strides'][0]
            layers.append({'layer':'Convolution1D', 'kernel_size':k_s, 'kernel_num':k_num, 'stride':stride, 'padding':0})
            
            if layer_descr['config']['use_bias']:
                layers.append({'layer':'Bias2D', 'units':k_num})
            self.__get_activation(layers, layer_descr)
            return layers
        
        elif 'Conv2D' == name:
            k_h = layer_descr['config']['kernel_size'][0]
            k_w = layer_descr['config']['kernel_size'][1]
            k_num = layer_descr['config']['filters']
            s_h = layer_descr['config']['strides'][1]
            s_v = layer_descr['config']['strides'][0]
            layers.append({'layer':'Convolution2D', 'kernel_height':k_h, 'kernel_width':k_w, 'kernel_num':k_num, 'stride_hz':s_h, 'stride_vl':s_v, 'padding_hz':0, 'padding_vl':0})
            
            if layer_descr['config']['use_bias']:
                layers.append({'layer':'Bias2D', 'units':k_num})
            self.__get_activation(layers, layer_descr)
            return layers 
            
        elif 'Cropping1D' == name:
            trimB = layer_descr['config']['cropping'][0]
            trimE = layer_descr['config']['cropping'][1]
            layers.append({'layer':'Cropping1D', 'trimBegin':trimB, 'trimEnd':trimE})
            return layers
            
        elif 'Cropping2D' == name:
            topTrim = layer_descr['config']['cropping'][0][0]
            bottomTrim = layer_descr['config']['cropping'][0][1]
            leftTrim = layer_descr['config']['cropping'][1][0]
            rightTrim = layer_descr['config']['cropping'][1][1]
            layers.append({'layer':'Cropping2D', 'topTrim':topTrim, 'bottomTrim':bottomTrim, 'leftTrim':leftTrim, 'rightTrim':rightTrim})
            return layers
            
        elif 'Activation' == name:
            self.__get_activation(layers, layer_descr)
            return layers
            
        elif 'Dense' == name:
            layers.append({'layer':'Dense2D', 'units':layer_descr['config']['units']})
            if layer_descr['config']['use_bias']:
                layers.append({'layer':'Bias2D', 'units':layer_descr['config']['units']})
            self.__get_activation(layers, layer_descr)
            return layers
            
        elif 'AveragePooling1D' == name:
            k_s = layer_descr['config']['pool_size'][0]
            stride = layer_descr['config']['strides'][0]
            layers.append({'layer':'AvgPooling1D', 'kernel_size':k_s, 'stride':stride, 'padding':0})
            return layers
            
        elif 'AveragePooling2D' == name:
            k_h = layer_descr['config']['pool_size'][0]
            k_w = layer_descr['config']['pool_size'][1]
            s_h = layer_descr['config']['strides'][1]
            s_v = layer_descr['config']['strides'][0]
            layers.append({'layer':'AvgPooling2D', 'kernel_height':k_h, 'kernel_width':k_w, 'stride_hz':s_h, 'stride_vl':s_v, 'padding_hz':0, 'padding_vl':0})
            return layers 
            
        elif 'MaxPooling1D' == name:
            k_s = layer_descr['config']['pool_size'][0]
            stride = layer_descr['config']['strides'][0]
            layers.append({'layer':'MaxPooling1D', 'kernel_size':k_s, 'stride':stride, 'padding':0})
            return layers
            
        elif 'MaxPooling2D' == name:
            k_h = layer_descr['config']['pool_size'][0]
            k_w = layer_descr['config']['pool_size'][1]
            s_h = layer_descr['config']['strides'][1]
            s_v = layer_descr['config']['strides'][0]
            layers.append({'layer':'MaxPooling2D', 'kernel_height':k_h, 'kernel_width':k_w, 'stride_hz':s_h, 'stride_vl':s_v, 'padding_hz':0, 'padding_vl':0})
            return layers
            
        elif 'GlobalMaxPooling1D' == name:
            layers.append({'layer':'GlobalMaxPooling1D'})
            return layers 
        
        elif 'GlobalMaxPooling2D' == name:
            layers.append({'layer':'GlobalMaxPooling2D'})
            return layers
        
        elif 'GlobalAveragePooling1D' == name:
            layers.append({'layer':'GlobalAveragePooling1D'})
            return layers 
        
        elif 'GlobalAveragePooling2D' == name:
            layers.append({'layer':'GlobalAveragePooling2D'})
            return layers
        
        elif 'Flatten' == name:
            layers.append({'layer':'Flatten'})
            return layers
            
        elif 'Reshape' == name:
            h = layer_descr['config']['target_shape'][0]
            w = layer_descr['config']['target_shape'][1]
            c = layer_descr['config']['target_shape'][2]
            layers.append({'layer':'Reshape', 'height':h, 'width':w, 'channel':c})
            return layers
        
        elif 'Permute' == name:
            dim1 = layer_descr['config']['dims'][0]
            dim2 = layer_descr['config']['dims'][1]
            dim3 = layer_descr['config']['dims'][2]
            layers.append({'layer':'Permute', 'dim1':dim1, 'dim2':dim2, 'dim3':dim3})
            return layers
            
        elif 'RepeatVector' == name:
            num = layer_descr['config']['n']
            layers.append({'layer':'RepeatVector', 'num':num})
            return layers
            
        else:
            raise NotImplementedError("Unknown layer type: " + name)  
    
    def __get_weight(self, weights, w_org, config):
        name = config['class_name']
        
        if 'Conv1D' == name:
            w = np.ndarray((1,w_org[self.idx].shape[0], w_org[self.idx].shape[1], w_org[self.idx].shape[2]))
            w[0,:,:, :] = w_org[self.idx][:,:,:]
            weights.append(w.tolist())
            self.idx += 1
            if config['config']['use_bias']:
                w = np.ndarray((1,1,1,w_org[self.idx].shape[0]))
                w[0,0,0, :] = w_org[self.idx][:]
                weights.append(w.tolist())
                self.idx += 1
        
        elif 'Conv2D' == name:
            weights.append(w_org[self.idx].tolist())
            self.idx += 1
            if config['config']['use_bias']:
                w = np.ndarray((1,1,1,w_org[self.idx].shape[0]))
                w[0,0,0, :] = w_org[self.idx][:]
                weights.append(w.tolist())
                self.idx += 1
                
        elif 'Dense' == name:
            w = np.ndarray((1,1,w_org[self.idx].shape[0], w_org[self.idx].shape[1]))
            w[0,0,:, :] = w_org[self.idx][:,:]
            weights.append(w.tolist())
            self.idx += 1
            if config['config']['use_bias']:
                w = np.ndarray((1,1,1,w_org[self.idx].shape[0]))
                w[0,0,0, :] = w_org[self.idx][:]
                weights.append(w.tolist())
                self.idx += 1
            
    def __get_activation(self, layers, layer_dscp):
        activation_name = layer_dscp['config']['activation']
        if activation_name == 'linear':
            pass
        elif activation_name == 'relu':
            layers.append({'layer':'ReLu'})
        elif activation_name == 'softmax':
            layers.append({'layer':'Softmax'})
        elif activation_name == 'elu':
            layers.append({'layer':'ELu'})
        elif activation_name == 'hard_sigmoid':
            layers.append({'layer':'HardSigmoid'})
        elif activation_name == 'sigmoid':
            layers.append({'layer':'Sigmoid'})
        elif activation_name == 'softplus':
            layers.append({'layer':'SoftPlus'})
        elif activation_name == 'softsign':
            layers.append({'layer':'SoftSign'})
        elif activation_name == 'tanh':
            layers.append({'layer':'TanH'})
        else:
            raise NotImplementedError("Unknown Activation type.")      
    
    def __save_json_string(self):
        with open(self.fname, 'w') as f:
            f.write(self.json_string)