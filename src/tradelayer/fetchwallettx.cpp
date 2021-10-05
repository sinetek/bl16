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

#include <boost/range/adaptor/reversed.hpp>

namespace mastercore
{
/**
 * Gets the byte offset of a transaction from the transaction index.
 */
unsigned int GetTransactionByteOffset(const uint256& txid)
{
    int position;

    LOCK(cs_main);

    // Read from the TXINDEX DB.
    if (pblocktree->Read(std::make_pair('t', txid), position)) {
        return position;
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
	std::map<std::string, uint256> mapResponse;

#ifdef ENABLE_WALLET
	CWalletRef pwalletMain = nullptr;
	pwalletMain = GetWallets()[0].get();

	if (!pwalletMain) {
		return mapResponse;
	}

	std::set<uint256> seenHashes;
	CWallet::TxItems txOrdered;
	{
		LOCK(pwalletMain->cs_wallet);
		txOrdered = pwalletMain->wtxOrdered;
	}

       	for (const auto& txp : ( txOrdered | boost::adaptors::reversed ))
	{
		const auto amount = txp.first;
		const auto& tx = txp.second;

		if (tx == nullptr) continue;
		
		const auto& txHash = tx->GetHash();

		{
			LOCK(cs_tally);
			if (!p_txlistdb->exists(txHash)) continue;
		}
		
		const auto& blockHash = tx->m_confirm.hashBlock;
		if (blockHash.IsNull()) continue;

		const CBlockIndex *blockindex = GetBlockIndex(blockHash);
		if (blockindex == nullptr) continue;

		int blockheight = tx->m_confirm.block_height;

		// Is this block in the right range?
		if (blockheight < startBlock || blockheight > endBlock) continue;

		int blockposition = GetTransactionByteOffset(txHash);
		std::string sortKey = strprintf("%07d%010d", blockheight, blockposition);
		mapResponse.insert(std::make_pair(sortKey, txHash));
		seenHashes.insert(txHash);
		if (mapResponse.size() >= count) break;
	}

	for ( auto& pend : my_pending )
	{
		const auto& txhash = pend.first;
		int blockheight = 9999999;
		if (blockheight < startBlock || blockheight > endBlock) continue;
		int blockposition = 0;

		{
			LOCK(pwalletMain->cs_wallet);
			auto walletIt = pwalletMain->mapWallet.find(txhash);
			if (walletIt != pwalletMain->mapWallet.end()) {
				auto& wtx = walletIt->second;
				blockposition = wtx.nOrderPos;
			}
		}

		std::string sortKey = strprintf("%07d%010d", blockheight, blockposition);
		mapResponse.insert(std::make_pair(sortKey, txhash));
	}

#endif /* ENABLE_WALLET */

	return mapResponse;
}


} // namespace mastercore
