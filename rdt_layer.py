from segment import Segment

# Base code taken from: https://canvas.oregonstate.edu/courses/1953681/assignments/9314394?module_item_id=23405011
# Duplicate check code: https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/

# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    # ################################################################################################################ #
    # in characters                     # The length of the string data that will be sent per packet...
    DATA_LENGTH = 4
    # in characters          # Receive window size for flow-control
    FLOW_CONTROL_WIN_SIZE = 15
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    # Use this for segment 'timeouts'
    currentIteration = 0
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    # ################################################################################################################ #

    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.currentIteration = 0
        # Add items as needed
        self.acknum = 0
        self.seqnum = self.acknum - \
            (self.FLOW_CONTROL_WIN_SIZE // self.DATA_LENGTH) * self.DATA_LENGTH
        self.messageDict = {}
        self.ackReceived = False  # switch this if correct ack is received from server
        self.updateAmount = (self.FLOW_CONTROL_WIN_SIZE //
                             self.DATA_LENGTH) * self.DATA_LENGTH  # make this a constant. how much to update by
        self.packetAmount = self.FLOW_CONTROL_WIN_SIZE // self.DATA_LENGTH
        self.countSegmentTimeouts = 0
        self.serverMessage = ""
        self.timeoutCounter = 0
        # counts how many missing iterations between send and ack receipt counts as a timeout
        # can adjust to make more or less stringent (ack could be delayed, resulting in more than one skips)
        self.timeoutThreshold = 1

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    # ################################################################################################################ #

    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################
    # setDataToSend()
    # Description:
    # Called by main to set the string data to send
    # ################################################################################################################
    def setDataToSend(self, data):
        self.dataToSend = data

    # ################################################################################################################
    # getDataReceived()
    # Description:
    # Called by main to get the currently received and buffered string data, in order
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...
        # ############################################################################################################ #
        return self.serverMessage

    # ################################################################################################################
    # processData()
    # Description:
    # "timeslice". Called by main once per iteration
    # ################################################################################################################
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################
    # processSend()
    # Description:
    # Manages Segment sending tasks
    # ################################################################################################################
    def processSend(self):
        if self.currentIteration == 1:  # just need to do this once, at beginning
            self.initialDataProcess()
        # basically, this should either be sending the same data and if an ack is received, update, then start over
        if self.dataToSend:
            if self.currentIteration % 3 == 0:
                if not self.ackReceived:  # if the expected ack hasn't come back from server
                    self.sendData()
                    if self.timeoutCounter > self.timeoutThreshold:
                        self.countSegmentTimeouts += 1
                    self.timeoutCounter += 1
                else:
                    # when ack expected comes back, add timeouts to timeoutcounter and clear it, then update ack and seq
                    self.updateSeqAndAck()
                    self.ackReceived = False
                    self.timeoutCounter = 0

        # keep sending the last bundle until and ack is received
        # only then, update seq and ack, which are the "sliding window"


# ################################################################################################################ #
# processReceive()                                                                                                 #
# Description:                                                                                                     #
# Manages Segment receive tasks                                                                                    #
# ################################################################################################################ #

    # info won't send early, so if you get a seqnum >= self.ack, update!
    # ackack is unecessary because it's implicit in that if you're getting the next batch, it got it


    def processReceiveAndSendRespond(self):
        """Responsible for receiving data and ack packets"""
        # probably would split this up more but this is how they wanted us to write it
        if not self.dataToSend:  # if no data to send, it's a server instance
            serverSideIncoming = self.receiveChannel.receive()
            for segment in serverSideIncoming:
                print(segment.to_string())

            # first, check through server side incoming segments.
            # no segments are sent early, so if we get one that has a seq >= than ack,
            # that means that the ack was received by the client and need to update server-side ack/seq

            # successful receipt flag. will return true or false depending on if checks are passed
            successfulReceipt = self.dataChecks(serverSideIncoming)

            if successfulReceipt:
                self.sendAck()
                self.updateData(serverSideIncoming)
                # if data is good AND the window still needs to be shifted, shift it
                for segment in serverSideIncoming:
                    if segment.seqnum > self.acknum:
                        self.updateAck()  # I think the trick to catch strict repeats is to update separately

# ############################################################################################################
# ############################################################################################################
        else:  # no data to send = back in client instance.
            # if receive correct ack, set self.ackReceived -> true
            clientSideIncoming = self.receiveChannel.receive()
            for segment in clientSideIncoming:
                if segment.acknum == self.acknum:
                    self.ackReceived = True

# ################################################################################################################ #
# HELPERS                                                                                                          #
# ################################################################################################################ #

    def sendData(self):
        """Called to send data from client instance"""
        localSeqnum = self.seqnum
        for _ in range(1, self.DATA_LENGTH):
            segmentSend = Segment()
            if localSeqnum < len(self.dataToSend):
                if localSeqnum < 0:
                    localSeqnum = 0
                segmentSend.setData(localSeqnum, self.messageDict[localSeqnum])
            else:
                segmentSend.setData(localSeqnum, 0)
            print("Sending segment: ", segmentSend.to_string())
            self.sendChannel.send(segmentSend)
            localSeqnum += self.DATA_LENGTH

    def sendAck(self):
        """Called to send data acknowledgement from server instance"""
        ackSegment = Segment()
        ackSegment.setAck(self.acknum)
        print("Sending ack: ", ackSegment.to_string())
        self.sendChannel.send(ackSegment)

    def updateSeqAndAck(self):
        """Called to update seqnum and acknum together"""
        self.seqnum += self.updateAmount
        self.acknum += self.updateAmount

    def updateAck(self):
        """Called to update just the ack"""
        self.acknum += self.updateAmount

    def updateData(self, verifiedSegments):
        # print('updating data!')
        """Called to add verified data to the message put together in the server"""
        for segment in verifiedSegments:
            if segment.payload != 0:  # the data of the dummy packets
                self.serverMessage += segment.payload
                self.seqnum += self.DATA_LENGTH
        self.getDataReceived()  # then call received to see if message is good
        # print('updated message:', self.serverMessage)

    def dataChecks(self, serverSideIncoming):
        """
        General function that performs several data checks. Basically, just returning true or false
        dpending on whether checks are passed or not.

        Checks performed:
        1. If number of packets received matches what's expected (packet drop/delay)
        2. Checks checksum of each packet (data corruption)
        3. Checks for duplicates (drop+delay)
        4. Checks that data was delivered in correct order (out-of-order packet delivery)
        5. Checks to make sure that data received follows last-received data to prevent data gaps
        """

        successfulReceipt = True  # default true. onus is on checks to change to false
        segmentSeqnums = []
        for segment in serverSideIncoming:
            segmentSeqnums.append(segment.seqnum)

        for segment in serverSideIncoming:
            if segment.seqnum <= self.seqnum:
                successfulReceipt = False

            # Citation: https://www.geeksforgeeks.org/python-ways-to-remove-duplicates-from-list/
            # generate duplicate check list. basically strips out seqnum from incoming packets
            # so they can be checked to see if there are duplicates
            duplicateCheck = []
            [duplicateCheck.append(x)
             for x in segmentSeqnums if x not in duplicateCheck]

            if len(duplicateCheck) != self.packetAmount:
                print('ERROR: Duplicate data detected!')
                successfulReceipt = False

            if not segment.checkChecksum():
                print('ERROR: Data corruption detected!')
                successfulReceipt = False

            # shallow check to see if amount of packets returning is correct
            if len(serverSideIncoming) != self.packetAmount:  # check that length is correct
                print('ERROR: Packet amount not what was expected!')
                print('Packet timed out or dropped.')
                successfulReceipt = False

            # for-each checks: check data integrity, use segment.seqnums to tally delays
            segmentSeqnums = []  # need this for checking order
            for segment in serverSideIncoming:  # check each segment's checksum for data corruption
                segmentSeqnums.append(segment.seqnum)
                if not segment.checkChecksum():
                    print('ERROR: Packets delivered out of order!')
                    successfulReceipt = False

            orderCheck = segmentSeqnums[0]
            for seqnum in segmentSeqnums:
                if orderCheck != seqnum:
                    successfulReceipt = False
                    print('ERROR: Packets delivered out of order!')
                orderCheck += self.DATA_LENGTH
                if len(segmentSeqnums) != self.packetAmount:
                    self.countSegmentTimeouts += 1
                    successfulReceipt = False

            # if everything else checks out, the first element's seqnum should equal the acknum
            # last annoying check
            if serverSideIncoming[0].seqnum != self.acknum:
                print('ERROR: Data gap detected!')
                successfulReceipt = False

        # return true or false depending on if checks passed or not
        return successfulReceipt

    def initialDataProcess(self):
        """
        Called during first iteration.
        Packages data string into dictionary, which is easier to work with
        """
        message = self.dataToSend  # all of the string
        # first chop up entire message and store as dictionary so can be sorted and packets
        seqnum = 0
        lengthCheck = 0
        rangeIndex = 0
        while lengthCheck < len(message):
            stringChunk = ""
            for _ in range(0, self.DATA_LENGTH):
                if rangeIndex < len(message):
                    stringChunk += message[rangeIndex]
                    rangeIndex += 1
            self.messageDict[seqnum] = stringChunk
            seqnum += self.DATA_LENGTH
            lengthCheck += RDTLayer.DATA_LENGTH  # incrementing by the length of each segment
