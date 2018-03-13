import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

def readdata(filename,printInfo = True):
    frame = pd.read_csv(filename)
    data = np.array(frame)
    print(data.shape)
    return data

def normaliz_SRTP(data,parameters = None):
    temp = data.copy()
    if parameters == None:
        parameters = {}
        parameters['Th1_mean'] = np.mean(data[:,0])
        parameters['Th1_std'] = np.std(data[:,0])
        parameters['Th2_mean'] = np.mean(data[:,2])
        parameters['Th2_std'] = np.std(data[:,2])
        parameters['W1_mean'] = np.mean(data[:,1])
        parameters['W1_std'] = np.std(data[:,1])
        parameters['W2_mean'] = np.mean(data[:,3])
        parameters['W2_std'] = np.std(data[:,3])
    temp[:,0] = (data[:,0]-parameters['Th1_mean'])/parameters['Th1_std'];
    temp[:,1] = (data[:,1]-parameters['W1_mean'])/parameters['W1_std'];
    temp[:,2] = (data[:,2]-parameters['Th2_mean'])/parameters['Th2_std'];
    temp[:,3] = (data[:,3]-parameters['W2_mean'])/parameters['W2_std'];
    temp[:,4] = data[:,4]/3
    temp[:,5] = data[:,5]/3
    return temp,parameters

def make_x_y_data(raw_X,raw_Y,num_periods = 1080,f_horizon  = 8):
    x_data = raw_X[:(len(raw_X) - (len(raw_X) % num_periods))]
    y_data = raw_Y[f_horizon:(len(raw_Y) - (len(raw_Y)% num_periods)) + f_horizon]
    return x_data,y_data

def create_one_test_set(x_data,y_data,num_periods = 1080):
    index = np.random.randint(0,x_data.shape[0]-num_periods)
    X_test = x_data[index:index+num_periods,:].reshape(-1,num_periods,6)
    Y_test = y_data[index:index+num_periods,:].reshape(-1,num_periods,2)
    return X_test,Y_test

def build_graph(num_periods = 1080,inputsize = 6,hidden = 50,output2 = 60,outputshape = 2,learning_rate = 0.00055,beta = 0.0015):
    tf.reset_default_graph()
    
    x = tf.placeholder(tf.float32,[None , num_periods,inputs])
    y = tf.placeholder(tf.float32,[None, num_periods,outputshape])

    #init_state = tf.get_variable("init_state",[None , num_periods,inputs],initializer = tf.contrib.layers.xavier_initializer())
    init_state = tf.get_variable("init_state",[1,hidden],initializer = tf.contrib.layers.xavier_initializer())

    basic_cell = tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu)


    rnn_output,states = tf.nn.dynamic_rnn(basic_cell,x,dtype = tf.float32,scope = 'basic_cell',initial_state = init_state);



    stacked_rnn_output = tf.reshape(rnn_output,[-1,hidden])
    #dropped_rnn_output = tf.nn.dropout(stacked_rnn_output,0.9)
    stacked_output = tf.layers.dense(stacked_rnn_output,output2,name = 'dense')

    output = tf.layers.dense(tf.nn.relu(stacked_output),
                         outputshape,name = 'dense2')

    outputs = tf.reshape(output,[-1,num_periods,outputshape])

    loss = tf.reduce_mean(tf.square(outputs[:,10:] - y[:,10:])) + beta*(tf.nn.l2_loss(tf.trainable_variables('basic_cell')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('dense')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('dense2')[0]))
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    training_op = optimizer.minimize(loss)
def trainnew(x_data,y_data,X_test,filename = 'try1',num_periods = 1080,inputsize = 6,hidden = 50,output2 = 60,outputshape = 2,learning_rate = 0.00055, beta = 0.0015,epochs = 2501):
    epochs = 2501
    mse = 0
    upperend = (x_data.shape[0] - 1500)//500 *500
    list1 = np.random.permutation(np.linspace(0,upperend,upperend//500 + 1,dtype = int))
    list1_length = len(list1)
    with tf.Session() as sess:
        init.run()
        for ep in range(epochs):
            rand1 = np.random.rand()
            if(rand1>0.5):
            #index = np.random.randint(0,x_data.shape[0]-num_periods)
                index = np.random.randint(0,upperend)
            else:
                index = list1[ep%list1_length]
            sess.run(training_op,feed_dict = {x:x_data[index:index+num_periods,:].reshape(-1,num_periods,inputs),
                                          y:y_data[index:index+num_periods,:].reshape(-1,num_periods,2)})
        #sess.run(training_op,feed_dict = {x:x_batches[batch:batch+1,::],y:y_batches[batch:batch+1,::]})
            if ep%20 == 0:
            #mse = loss.eval(feed_dict = {x:x_batches[batch:batch+1,::],y:y_batches[batch:batch+1,::]})
                mse += loss.eval(feed_dict = {x:x_data[index:index+num_periods,:].reshape([1,num_periods,inputs]),
                                          y:y_data[index:index+num_periods,:].reshape([1,num_periods,2])})
            if ep%100 == 0:
                mse /= 5
                print(ep,"\tMSE:",mse)
                mse = 0
        y_pred = sess.run(outputs,feed_dict = {x:X_test})
        init_params = sess.run(tf.trainable_variables('init_state'))
        rnn_params = sess.run(tf.trainable_variables('basic_cell'))
        dense1_params = sess.run(tf.trainable_variables('dense'))
        dense2_params = sess.run(tf.trainable_variables('dense2'))
        saver = tf.train.Saver()
        save_path = saver.save(sess, "checkpointset\\try1");
    NNparams = {}
    NNparams['init_params'] = init_params
    NNparams['rnn_params'] = rnn_params
    NNparams['dense1_params'] = dense1_params
    NNparams['dense2_params'] = dense2_params
    return NNparams,y_pred