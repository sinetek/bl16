#ifndef RPC_H
#define RPC_H

#include <univalue.h>
class JSONRPCRequest;

void PopulateFailure(int error);
UniValue tl_getwalletbalance(const JSONRPCRequest& request);
UniValue tl_getallbalancesforaddress(const JSONRPCRequest& request);

#endif

