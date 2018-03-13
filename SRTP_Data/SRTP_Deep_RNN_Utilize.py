import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf

def read_data(filename,row_start = 0,row_end = None,column_start = 0, column_end = None,print_shape = True):
    rawdata = np.array(pd.read_csv(filename))
    if(row_end == None):
        rawdata = rawdata[row_start:,:]
    else:
        rawdata = rawdata[row_start:row_end,:]
    if(column_start == None):
        rawdata = rawdata[:,column_start:];
    else:
        rawdata = rawdata[:,column_start:column_end];
    if(print_shape):
        print(rawdata.shape);
    rawdata[:,2] = -(rawdata[:,2]+180)
    rawdata[:,3] = -(rawdata[:,3])
    return rawdata

def srtp_simple_visualize(data,start,end,newfigure = True):
    picnum = 6
    if(newfigure):
        plt.figure(22,figsize = (18,picnum*5.4))
    else:
        plt.clf()
    plt.subplot(611)
    plt.plot(pd.Series((data[start:end,0])),"bo",markersize = 1,label = 'Angle1')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(612)
    plt.plot(pd.Series((data[start:end,2])),"bo",markersize = 1,label = 'Angle2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(613)
    plt.plot(pd.Series((data[start:end,0] - data[start:end,2])),"bo",markersize = 1,label = 'A1 - A2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(614)
    plt.plot(pd.Series((data[start:end,4])),"bo",markersize = 1,label = 'spike1')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(615)
    plt.plot(pd.Series((data[start:end,5])),"bo",markersize = 1,label = 'spike2')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.subplot(616)
    plt.plot(pd.Series((data[start:end,6])),"bo",markersize = 1,label = 'spike3')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.show()

def srtp_inter_draw(data,range_list):
    termnum = len(range_list)/2;
    i = 0
    handle = 'fuck'
    mistake = 0;
    start = 0
    end = range_list[2*i]*6000 + range_list[2*i+1]*100
    srtp_simple_visualize(data,start,end)
    handle = input('what to do next\n')
    while(i<termnum and (not handle == 'q')):
        if(handle == '' or 'next' in handle):
            start = range_list[2*i]*6000 + range_list[2*i+1]*100
            i += 1
            if(i<termnum):
                end =  range_list[2*i]*6000 + range_list[2*i+1]*100;
                srtp_simple_visualize(data,start,end,False)
                handle = input('what to do next\n')
            else:
                print('No more event')
                handle = 'q'
        elif(',' in handle):
            startdis = int(handle.split(',')[0])
            enddis = int(handle.split(',')[1])
            start += startdis
            end += enddis
            srtp_simple_visualize(data,start,end,False)
            handle = input('what to do next\n')
        elif('back' in handle):
            if(i==0):
                start = 0
            else:
                start = range_list[2*i - 2]*6000 + range_list[2*i-1]*100
            end = range_list[2*i]*6000 + range_list[2*i+1]*100
            srtp_simple_visualize(data,start,end,False)
            handle = input('what to do next\n')
        elif(mistake > 0):
            handle = 'q'
        else:
            mistake += 1
            print('Wrong input')
            handle = input('what to do next\n')

def print_info(data):
    for i in range(7):
        if(i==0):
            print('angle1')
        if(i==1):
            print('omega1')
        if(i==2):
            print('angle2')
        if(i==3):
            print('omega2')
        if(i>3):
            print('spike',i-3)
        print('mean:,',data[:,i].mean())
        print('std:,',data[:,i].std())

def print_y_info(data_dict):
    for i in range(1,5):
        print('y',i)
        print(data_dict['truey' + str(i)].mean())
        print(data_dict['truey' + str(i)].std())


def new_train(data_dict,ckptname,epochs=201,learning_rate=0.0001,beta = 0.001,cluster_num = 12,filenum = 4,inputs = 7,hidden = 30,output2 = 25,output3 = 12,output4 =15,outputshape = 1,num_periods = 1080):
    num_periods = 1080
    tf.reset_default_graph()
    num_periods = 1080
    x = tf.placeholder(tf.float32,[None,1080,inputs])
    y = tf.placeholder(tf.float32,[None,1080,outputshape]);
    cells = [];
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    #cells.append(tf.contrib.rnn.BasicRNNCell(num_units = 40,activation = tf.nn.relu))
    #cells.append(tf.contrib.rnn.BasicRNNCell(num_units = 30,activation = tf.nn.relu))
    #Qcells.append(tf.contrib.rnn.BasicRNNCell(num_units = 20,activation = tf.nn.relu))
        
    cells = tf.contrib.rnn.MultiRNNCell(cells)

    rnn_output,states = tf.nn.dynamic_rnn(cells,x,dtype = tf.float32,scope = 'cells');
    stacked_rnn_output = tf.reshape(rnn_output,[-1,hidden])
    stacked_output = tf.layers.dense(stacked_rnn_output,output2,name = 'dense')
    hidden_dense = tf.layers.dense(tf.nn.relu(stacked_output),
                              output3,name = 'hidden_dense')
    output = tf.layers.dense(tf.nn.relu(hidden_dense),
                         outputshape,name = 'dense2')
    outputs = tf.reshape(output,[-1,num_periods,outputshape])
    loss = tf.reduce_mean(tf.square(outputs[:,10:] - y[:,10:])) + beta*(tf.nn.l2_loss(tf.trainable_variables('cells')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('dense')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('hidden_dense')[0])+
                                                 tf.nn.l2_loss(tf.trainable_variables('dense2')[0]))
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    training_op = optimizer.minimize(loss)
    init = tf.global_variables_initializer()
    
    List1 = []
    x_data = np.zeros((cluster_num,num_periods,inputs))
    y_data = np.zeros((cluster_num,num_periods,outputshape))
    mse = 0
    for i in range(1,2*filenum + 1):
        List1.append(data_dict['datax' + str(i)].shape[0] - 1080)

    with tf.Session() as sess:
        init.run()

        for ep in range(epochs):
            source = np.random.randint(1,2*filenum + 1,cluster_num,dtype = int)
            for i in range(cluster_num):
                index = np.random.randint(0,List1[source[i]-1])
            #index = np.random.randint(0,List1[source-1],cluster_num,dtype = int)
            #for i in range(cluster_num):
                x_data[i,:,:] = data_dict['datax' + str(source[i])][index:index+num_periods,:]
                y_data[i,:,:] = data_dict['datay' + str(source[i])][index:index+num_periods,:]
            sess.run(training_op,feed_dict = { x:x_data,y:y_data})
            if ep%10 == 0:
                mse +=loss.eval(feed_dict = {x:x_data,y:y_data})
            if ep%100 == 0:
                mse /= 10
                print(ep,"\tMSE:",mse)
                mse = 0

        rnn_params = sess.run(tf.trainable_variables('cells'))
        dense1_params = sess.run(tf.trainable_variables('dense'))
        hidden_dense_params = sess.run(tf.trainable_variables('hidden_dense'))
        dense2_params = sess.run(tf.trainable_variables('dense2'))
        saver = tf.train.Saver()
        save_path = saver.save(sess, "checkpointset\\"+ ckptname);
        
def continue_training(data_dict,ckptname,epochs=201,learning_rate=0.0001,beta = 0.001,cluster_num = 12,filenum = 4,saveckptname = None,inputs = 7,hidden = 30,output2 = 25,output3 = 12,output4 =15,outputshape = 1,num_periods = 1080):
    if(saveckptname == None):
        saveckptname = ckptname
    
    tf.reset_default_graph()
    num_periods = 1080
    x = tf.placeholder(tf.float32,[None,1080,inputs])
    y = tf.placeholder(tf.float32,[None,1080,outputshape]);
    #cells = [];

    #for i in range(3):
    #    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
        
    cells = [];
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
        
    #cells = tf.contrib.rnn.MultiRNNCell(cells)
    cells = tf.contrib.rnn.MultiRNNCell(cells)
    

    rnn_output,states = tf.nn.dynamic_rnn(cells,x,dtype = tf.float32,scope = 'cells');
    stacked_rnn_output = tf.reshape(rnn_output,[-1,hidden])
    stacked_output = tf.layers.dense(stacked_rnn_output,output2,name = 'dense')
    hidden_dense = tf.layers.dense(tf.nn.relu(stacked_output),
                              output3,name = 'hidden_dense')
    output = tf.layers.dense(tf.nn.relu(hidden_dense),
                         outputshape,name = 'dense2')
    outputs = tf.reshape(output,[-1,num_periods,outputshape])
    loss = tf.reduce_mean(tf.square(outputs[:,10:] - y[:,10:])) + beta*(tf.nn.l2_loss(tf.trainable_variables('cells')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('dense')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('hidden_dense')[0])+
                                                 tf.nn.l2_loss(tf.trainable_variables('dense2')[0]))
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    gvs = optimizer.compute_gradients(loss)
    capped_gvs = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gvs]
    #capped_gvs = tf.clip_by_value(gvs, -5, 5, name=None)
    training_op = optimizer.apply_gradients(capped_gvs)
    
    mse = 0
    cluster_num = 8
    List1 = []
    x_data = np.zeros((cluster_num,num_periods,inputs))
    y_data = np.zeros((cluster_num,num_periods,outputshape))
    for i in range(1,2*filenum + 1):
        List1.append(data_dict['datax' + str(i)].shape[0] - 1080)

    with tf.Session() as sess:
        saver=tf.train.Saver()
        checkpoint_filepath = 'checkpointset\\'+ckptname
        saver.restore(sess,checkpoint_filepath);
        for ep in range(epochs):
            source = np.random.randint(1,2*filenum + 1,cluster_num,dtype = int)
            for i in range(cluster_num):
                index = np.random.randint(0,List1[source[i]-1])
            #index = np.random.randint(0,List1[source-1],cluster_num,dtype = int)
            #for i in range(cluster_num):
                x_data[i,:,:] = data_dict['datax' + str(source[i])][index:index+num_periods,:]
                y_data[i,:,:] = data_dict['datay' + str(source[i])][index:index+num_periods,:]
            sess.run(training_op,feed_dict = { x:x_data,y:y_data})
            if ep%10 == 0:
                mse +=loss.eval(feed_dict = {x:x_data,y:y_data})
            if ep%100 == 0:
                mse /= 10
                print(ep,"\tMSE:",mse)
                mse = 0
        rnn_params = sess.run(tf.trainable_variables('cells'))
        dense1_params = sess.run(tf.trainable_variables('dense'))
        hidden_dense_params = sess.run(tf.trainable_variables('hidden_dense'))
        dense2_params = sess.run(tf.trainable_variables('dense2'))
        saver = tf.train.Saver()
        save_path = saver.save(sess, "checkpointset\\"+ saveckptname);
    return rnn_params,dense1_params,hidden_dense_params,dense2_params
def numpy_verifying(testx,testy,start,end,rnn_params,dense1_params,hidden_dense_params,dense2_params,):
    params_list = []
    rnnW1 = rnn_params[0]
    rnnb1 = rnn_params[1].reshape(1,-1)
    rnnW2 = rnn_params[2]
    rnnb2 = rnn_params[3].reshape(1,-1)
    rnnW3 = rnn_params[4]
    rnnb3 = rnn_params[5].reshape(1,-1)
    denseW1 = dense1_params[0]
    denseb1 = dense1_params[1].reshape(1,-1)
    denseW2 = hidden_dense_params[0]
    denseb2 = hidden_dense_params[1].reshape(1,-1)
    denseW3 = dense2_params[0]
    denseb3 = dense2_params[1].reshape(1,-1)
    
    params_list = [rnnW1,rnnb1,rnnW2,rnnb2,rnnW3,denseW1,denseb1,denseW2,denseb2,denseW3,denseb3]

    inputsize = testx.shape[1]

    hiddensize = rnnW1.shape[1]
    rnnsize2 = rnnW2.shape[1]
    rnnsize3 = rnnW3.shape[1]
    hiddenlayersize = len(denseb1)
    rnn_state_size = len(rnnb1)
    #outputsize = 2
    outputsize = len(denseb3)
    Test_input = np.zeros((1,inputsize+hiddensize))
    #State = np.copy(init_params[0])
    State1 = np.zeros((1,hiddensize))
    State2 = np.zeros((1,rnnsize2))
    State3 = np.zeros((1,rnnsize3))
    temp_input = np.zeros((1,hiddensize + rnnsize2));
    temp_input2 = np.zeros((1,rnnsize2 + rnnsize3));



    finaloutput = np.zeros((testx.shape[0],outputsize))
    for i in range(testx.shape[0]):
        Test_input[0,:inputsize] = testx[i,:].T
        Test_input[0,inputsize:] = State1
        #Test_input[0,:hiddensize] = State
        #Test_input[0,hiddensize:] = x_data[i,:].T
        #State = Test_input.dot(U1.dot(N)) + b1
        State1 = Test_input.dot(rnnW1) + rnnb1
        State1[State1<0] = 0

        temp_input[0,0:hiddensize] = State1
        temp_input[0,hiddensize:] = State2
        State2 = temp_input.dot(rnnW2) + rnnb2
        State2[State2<0] = 0

        temp_input2[0,0:rnnsize2] = State2
        temp_input2[0,rnnsize2:] = State3
        State3 = temp_input2.dot(rnnW3) + rnnb3
        State3[State3<0] = 0
        #hidden = State.dot(U1.dot(N))+b2 

        hidden = State3.dot(denseW1)+denseb1 
        hidden[hidden<0] = 0

        hidden2 = hidden.dot(denseW2) + denseb2
        hidden2[hidden2<0] = 0

    #    hidden3 = hidden2.dot(denseW3) + denseb3
    #    hidden3[hidden3<0] = 0

        tempoutput = hidden2.dot(denseW3) + denseb3
        finaloutput[i,:] = np.copy(tempoutput)

    RNNmse = np.mean(np.square(finaloutput[start:end,:] - testy[start:end,:])*stdy**2)
    RNNmse2 = np.mean(np.square(finaloutput[start:end,:] - testy[start:end,:]))


    #another naive method
    naivey = np.zeros(testy.shape)
    naivey[:,0] = ((testx[:,0]*std1 + mean1 + (testx[:,1]*stdw1+meanw1)*0.08)
                   - (testx[:,2]*std2 + mean2 + (testx[:,3]*stdw2+meanw2)*0.08))
    #naivey[:,1] = (testx[:,2]*std2 + mean2 + (testx[:,3]*stdw2+meanw2)*0.08 - mean2)/std2
    naivemse1 = np.mean(np.square(naivey[start:end,:] - testy[start:end,:]*stdy-meany))
    naivey2 = np.zeros(testy.shape)
    naivey2[:,0] = testx[:,0]*std1 + mean1 - (testx[:,2]*std2 + mean2)
    naivemse2 = np.mean(np.square(naivey2[start:end,:] - testy[start:end,:]*stdy - meany));


    print("RNN mse:",RNNmse)
    print("RNN normalized mse",RNNmse2)
    print("naive mse:",np.min((naivemse1,naivemse2)))
    print()
    plt.figure(1,figsize = (18,1*5.4))
    plt.subplot(111)
    plt.title("Angle1 Forecast vs Actual",fontsize = 14)

    plt.plot(pd.Series(testx[start:end,0]*std1+mean1 - testx[start:end,2]*std2-mean2),'y-',markersize = 1,label = 'Current Info')
    plt.plot(pd.Series(np.ravel(testy[start:end,0]*stdy+meany)),"b-",markersize = 1,label = 'Actual')
    plt.plot(pd.Series(np.ravel(finaloutput[start:end,0]*stdy+meany)),"r-",markersize = 1,label = 'Forecast')
    plt.plot(pd.Series(naivey[start:end,0]),'g-',markersize = 1,label = 'naive guess')
    plt.legend(loc = "upper left")
    plt.xlabel("Time Periods")

    plt.show()
    return params_list

def continue_training_larger_loss(data_dict,ckptname,epochs=201,learning_rate=0.0001,beta = 0.001,cluster_num = 12,filenum = 4,saveckptname = None,inputs = 7,hidden = 30,output2 = 25,output3 = 12,output4 =15,outputshape = 1,num_periods = 1080,ratio = 0):
    if(saveckptname == None):
        saveckptname = ckptname
    
    tf.reset_default_graph()
    num_periods = 1080
    x = tf.placeholder(tf.float32,[None,1080,inputs])
    y = tf.placeholder(tf.float32,[None,1080,outputshape]);
    #cells = [];

    #for i in range(3):
    #    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
        
    cells = [];
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
    cells.append(tf.contrib.rnn.BasicRNNCell(num_units = hidden,activation = tf.nn.relu))
        
    #cells = tf.contrib.rnn.MultiRNNCell(cells)
    cells = tf.contrib.rnn.MultiRNNCell(cells)
    

    rnn_output,states = tf.nn.dynamic_rnn(cells,x,dtype = tf.float32,scope = 'cells');
    stacked_rnn_output = tf.reshape(rnn_output,[-1,hidden])
    stacked_output = tf.layers.dense(stacked_rnn_output,output2,name = 'dense')
    hidden_dense = tf.layers.dense(tf.nn.relu(stacked_output),
                              output3,name = 'hidden_dense')
    output = tf.layers.dense(tf.nn.relu(hidden_dense),
                         outputshape,name = 'dense2')
    outputs = tf.reshape(output,[-1,num_periods,outputshape])
    loss = tf.reduce_mean(tf.square(tf.square(outputs[:,10:] - y[:,10:]))) + beta*(tf.nn.l2_loss(tf.trainable_variables('cells')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('cells')[2])+
                                                tf.nn.l2_loss(tf.trainable_variables('cells')[4])+
                                                tf.nn.l2_loss(tf.trainable_variables('dense')[0])+
                                                tf.nn.l2_loss(tf.trainable_variables('hidden_dense')[0])+
                                                 tf.nn.l2_loss(tf.trainable_variables('dense2')[0]))
    MSE = tf.reduce_mean(tf.square(outputs[:,10:] - y[:,10:]))
    
    loss = tf.add(loss,MSE*ratio)
    optimizer = tf.train.AdamOptimizer(learning_rate = learning_rate)
    gvs = optimizer.compute_gradients(loss)
    capped_gvs = [(tf.clip_by_value(grad, -1., 1.), var) for grad, var in gvs]
    #capped_gvs = tf.clip_by_value(gvs, -5, 5, name=None)
    training_op = optimizer.apply_gradients(capped_gvs)
    
    mse = 0
    cluster_num = 8
    List1 = []
    x_data = np.zeros((cluster_num,num_periods,inputs))
    y_data = np.zeros((cluster_num,num_periods,outputshape))
    for i in range(1,2*filenum + 1):
        List1.append(data_dict['datax' + str(i)].shape[0] - 1080)

    with tf.Session() as sess:
        saver=tf.train.Saver()
        checkpoint_filepath = 'checkpointset\\'+ckptname
        saver.restore(sess,checkpoint_filepath);
        for ep in range(epochs):
            source = np.random.randint(1,2*filenum + 1,cluster_num,dtype = int)
            for i in range(cluster_num):
                index = np.random.randint(0,List1[source[i]-1])
            #index = np.random.randint(0,List1[source-1],cluster_num,dtype = int)
            #for i in range(cluster_num):
                x_data[i,:,:] = data_dict['datax' + str(source[i])][index:index+num_periods,:]
                y_data[i,:,:] = data_dict['datay' + str(source[i])][index:index+num_periods,:]
            sess.run(training_op,feed_dict = { x:x_data,y:y_data})
            if ep%10 == 0:
                mse += MSE.eval(feed_dict = {x:x_data,y:y_data})
            if ep%100 == 0:
                mse /= 10
                print(ep,"\tMSE:",mse)
                mse = 0
        rnn_params = sess.run(tf.trainable_variables('cells'))
        dense1_params = sess.run(tf.trainable_variables('dense'))
        hidden_dense_params = sess.run(tf.trainable_variables('hidden_dense'))
        dense2_params = sess.run(tf.trainable_variables('dense2'))
        saver = tf.train.Saver()
        save_path = saver.save(sess, "checkpointset\\"+ saveckptname);
    return rnn_params,dense1_params,hidden_dense_params,dense2_params