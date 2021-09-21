/**
 * @file fetchwallettx.cpp
 *
 * The fetch functions provide a sorted list of transaction hashes ordered by block,
 * position in block and position in wallet including STO receipts.
 */

#include <tradelayer/fetchwallettx.h>

#include <tradelayer/log.h>
#include <tradelayer/pending.h>
#include <tradelayer/tradelayer.h>
#include <tradelayer/utilsbitcoin.h>

#include <init.h>
#include <sync.h>
#include <tinyformat.h>
#include <txdb.h>
#include <validation.h>
#ifdef ENABLE_WALLET
#include <wallet/wallet.h>
#endif

#include <list>
#include <map>
#include <set>
#include <stdint.h>
#include <string>
#include <utility>
#include <vector>

namespace mastercore
{
/**
 * Gets the byte offset of a transaction from the transaction index.
 */
unsigned int GetTransactionByteOffset(const uint256& txid)
{
    LOCK(cs_main);

    CDiskTxPos position;
    if (pblocktree->ReadTxIndex(txid, position)) {
        return position.nTxOffset;
    }

    return 0;
}

/**
 * Returns an ordered list of Trade Layer transactions including STO receipts that are relevant to the wallet.
 *
 * Ignores order in the wallet (which can be skewed by watch addresses) and utilizes block height and position within block.
 */
std::map<std::string, uint256> FetchWalletTLTransactions(unsigned int count, int startBlock, int endBlock)
{
#warning xxx
}


} // namespace mastercore
