from datetime import datetime
from typing import Dict, List, Optional
import uuid

class Proposal:
    """提案管理类"""
    def __init__(self, title: str, description: str, proposal_id: Optional[str] = None):
        self.proposal_id = proposal_id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.votes = {"support": 0, "oppose": 0}
        self.voters = set()  # 记录已投票用户
        self.created_at = datetime.now().isoformat()
        self.status = "active"  # active, closed
        self.comments = []
    
    def add_vote(self, voter_id: str, vote: str) -> bool:
        """添加投票
        
        Args:
            voter_id: 投票者ID
            vote: 投票选择 ('support' 或 'oppose')
        """
        if self.status != "active":
            return False
            
        if voter_id in self.voters:
            return False
            
        if vote not in ["support", "oppose"]:
            return False
            
        self.votes[vote] += 1
        self.voters.add(voter_id)
        return True
    
    def add_comment(self, voter_id: str, comment: str) -> bool:
        """添加评论"""
        if self.status != "active":
            return False
            
        self.comments.append({
            "voter_id": voter_id,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        })
        return True
    
    def close_proposal(self):
        """关闭提案"""
        self.status = "closed"
    
    def get_results(self) -> Dict:
        """获取投票结果"""
        total = sum(self.votes.values())
        support_percentage = (self.votes["support"] / total * 100) if total > 0 else 0
        oppose_percentage = (self.votes["oppose"] / total * 100) if total > 0 else 0
        
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "description": self.description,
            "votes": self.votes,
            "total_votes": total,
            "support_percentage": support_percentage,
            "oppose_percentage": oppose_percentage,
            "status": self.status,
            "comments": self.comments
        }


class ProposalManager:
    """提案管理器"""
    def __init__(self):
        self.proposals = {}
    
    def create_proposal(self, title: str, description: str) -> Proposal:
        """创建新提案"""
        proposal = Proposal(title, description)
        self.proposals[proposal.proposal_id] = proposal
        return proposal
    
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """获取指定提案"""
        return self.proposals.get(proposal_id)
    
    def list_proposals(self, status: Optional[str] = None) -> List[Dict]:
        """列出所有提案"""
        proposals = []
        for p_id, proposal in self.proposals.items():
            if status is None or proposal.status == status:
                proposals.append({
                    "proposal_id": p_id,
                    "title": proposal.title,
                    "status": proposal.status,
                    "created_at": proposal.created_at,
                    "vote_count": sum(proposal.votes.values())
                })
        return proposals
    
    def close_proposal(self, proposal_id: str) -> bool:
        """关闭提案"""
        proposal = self.get_proposal(proposal_id)
        if proposal:
            proposal.close_proposal()
            return True
        return False