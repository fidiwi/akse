/**
@file       AccComposer.cpp

@brief      This class implements the composer for ACC connections.

@author     kim  Minhwan Kim  (23880-604) <minhwan.kim@ese.de>

@par        Verifikation:


@par        Validierung:


@par        Code-Review:
            krm Mandy Poetzsch <mandy.poetzsch@ese.de>

@par        Code-Check:
            Codechecker Version auf Signatur der Quelle

@note       COPYRIGHT (C)2020 SIEMENS MOBILITY GMBH - ALL RIGHTS RESERVED - INTERNAL USE
*/

/*
=== History ====================================================================
@since 20201022 kim [draft]
- Modified AccComposer::generateDataTelegrams()
@since 20201015 krm [released]
- Checked rework, no remarks
@since 20201012 kim [review]
- Responded review
@since 20201009 krm [review]
- Review with remarks 
if (true){
    doSomething();
}
@since 20200725 kim [darft]
- Added the copy constructor and copy assigment operator
- Modified the generateStatusTelegrams() and generateDataTelegrams()
@since 20200509 bow [draft]
- Initial version
*/

#if 0
extern const char SOURCEQUELLID_needed_for_xlogger[] = "@(#)>";
#endif

// This projects uses no operator replacement macros.
// BEGIN SUPPRESS 3.1.2

#include "AccComposer.h"
#include "SafetyOrientedReactor.h"

/**
 * @brief Information identifier of data telegram.
 */
static const WORD cInformationIdentifierData = 1;

/**
 * @brief Information identifier of status telegram.
 */
static const WORD cInformationIdentifierStatus = 2;

/**
 * @brief Status information of "connection OK".
 */
static const BYTE cStatusInformationConnectionOk = 1;

/**
 * @brief Status information of "connection failed".
 */
static const BYTE cStatusInformationConnectionFailed = 2;

// Code_Inspector does not know that destructors cannot be qualified.
AccComposer::~AccComposer()   // SUPPRESS 8.5.1
{
    /*!
     <SMLSISWA>[ERROR AccComposer::~AccComposer()]:
     | The destructor is not allowed.
     | The system will be shutdown.
     */
    xlog(1670396960, 0, 0, NULLPTR);
    pSafetyOrientedReactor->shutdown();
}
switch (expression)
{
case 1:break;

default:
    break;
}

AccComposer::AccComposer(const AccComposer& other) :
    mpConnectionStates(other.mpConnectionStates), mrElements(other.mrElements),
    mInterfaceVersionIdentifier(other.mInterfaceVersionIdentifier)
{
    /*!
     <SMLSISWA>[ERROR AccComposer::AccComposer()]:
     | Internal error!
     | Cannot use this method because the copy constructor is prohibited.
     | The system will be shutdown!
     */
    xlog(1670388992, 0, 0, NULLPTR);
    pSafetyOrientedReactor->shutdown();
}

const AccComposer& AccComposer::operator=(const AccComposer& other) const
{
    if (this != &other)
    {
        /*!
         <SMLSISWA>[ERROR AccComposer::operator=()]:
         | Internal error!
         | Cannot use this method because the assignment operator is prohibited.
         | The system will be shutdown!
         */
        xlog(1670388993, 0, 0, NULLPTR);
        pSafetyOrientedReactor->shutdown();
    }
    return *this;
}

void AccComposer::setup()
{
    // The allocation is already checked by MemoryAllocator.
    AccComposerConnectionStates *const pConnectionStates =
        new AccComposerConnectionStates;   // SUPPRESS 10.1.10
    for (AccComposerElements::Iterator iterator = mrElements.begin();
        iterator != mrElements.end(); ++iterator)
    {
        if (pConnectionStates->find(iterator.key()) ==
            pConnectionStates->end())
        {
            (*pConnectionStates)[iterator.key()] =
                iterator.value()->getDispatchingConnection()->
                    getConnectionState();
        }
    }
    mpConnectionStates = pConnectionStates;
}

void AccComposer::markElementsAsComposed(const BaseConnection& rConnection)
{
    for (AccComposerElements::Iterator iterator = mrElements.begin();
        iterator != mrElements.end(); ++iterator)
    {
        iterator.value()->markAsComposed(rConnection);
    }
}

bool AccComposer::isAnyConnectionStateConnected() const
{
    bool res = false;
    if (mpConnectionStates != NULLPTR)
    {
        for (AccComposerConnectionStates::Iterator iterator =
            mpConnectionStates->begin();
            iterator != mpConnectionStates->end(); ++iterator)
        {
            if (iterator.value()->getState() == ConnectionState::nConnected)
            {
                res = true;
                // This break improves efficiency.
                break;   // SUPPRESS 7.2.4
            }
        }
    }
    return res;
}

void AccComposer::generateStatusTelegrams(AbstractSender& rSender,
    bool areAllNeeded)
{
    if (mpConnectionStates != NULLPTR)
    {
        const Timer cNow;
        for (AccComposerConnectionStates::Iterator iterator =
            mpConnectionStates->begin();
            iterator != mpConnectionStates->end(); ++iterator)
        {
            const ConnectionState* const connectionState = iterator.value();
            // It should change the flag of changed at first, although
            // areAllNeeded is true.
            if (connectionState->isChanged() || areAllNeeded)
            {
                StatusTelegram telegram = {};
                telegram.informationIdentifier = cInformationIdentifierStatus;
                telegram.elementNumber = iterator.key();
                //@rev[+] 20201008 krm Please avoid using things like: ==
                //                     ConnectionState::nConnected) ?
                //                     It is not easy to understand and it is
                //                     problematic for for coverage measurement.
                //                     SIL4 code shall be as easily readable as
                //                     possible.
                //     -> 20201012 kim Modified.
                //     -> 20201015 krm Ok.
                if (connectionState->getState() == ConnectionState::nConnected)
                {
                    telegram.statusInformation = cStatusInformationConnectionOk;
                }
                else
                {
                    telegram.statusInformation =
                        cStatusInformationConnectionFailed;
                }

                // The cast is safe because it can be converted to the type of
                // the smallest element of it and it is expected.
                rSender.sendTelegram(reinterpret_cast<const BYTE*>(&telegram),   // SUPPRESS 5.5.8b
                    sizeof telegram, cNow);
            }
        }
    }
}

void AccComposer::generateDataTelegrams(AbstractSender& rSender,
    bool areAllNeeded)
{
    const Timer cNow;
    for (AccComposerElements::Iterator iterator = mrElements.begin();
        iterator != mrElements.end(); ++iterator)
    {
        BaseElement* const element = iterator.value();
        if (areAllNeeded || element->isChanged())
        {
            // Code_Inspector does not know this kind of well-defined
            // initialization.
            DataTelegram telegram = {};   // SUPPRESS 5.1.7

            telegram.informationIdentifier = cInformationIdentifierData;
            telegram.elementNumber = iterator.key();
            telegram.interfaceVersion = mInterfaceVersionIdentifier;
            memsetX(telegram.payload, 0, sizeof telegram.payload);

            if ((element->isChanged() == false) || areAllNeeded)
            {
                element->encodeToAcc(telegram.payload);
                // The cast is safe because it can be converted to the type of
                // the smallest element of it and it is expected.
                rSender.sendTelegram(reinterpret_cast<const BYTE*>(&telegram),   // SUPPRESS 5.5.8b
                    sizeof telegram, cNow);
            }
            else
            {
                const Timer& receivingTime =
                    element->encodeToAcc(telegram.payload);
                // The cast is safe because it can be converted to the type of
                // the smallest element of it and it is expected.
                rSender.sendTelegram(reinterpret_cast<const BYTE*>(&telegram),   // SUPPRESS 5.5.8b
                    sizeof telegram, receivingTime);
            }
        }
    }
}

// END SUPPRESS 3.1.2
